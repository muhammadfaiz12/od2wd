from src.mapper import mapProperty, mpRankWTypeSim
import csv
import pandas as pd
from src.wikimedia import searchEntity, searchObjWProperty, searchProperty, searchPropertyRange
from dateutil.parser import parse
import operator
import re
import numpy as np
import sys, os, requests, json
import scipy.stats 
from dateutil.parser import parse
import var_settings

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False
    except OverflowError:
        return False

def load_data(file_name,folder):
    df = pd.read_csv("data/{}/{}".format(folder,file_name), encoding='latin-1')
    return df

def ranking(candidateList, goal, flag, propertyLbl,threshold=0):
    scoreList = [0] * len(candidateList)
    for i in range(len(candidateList)):
        results = searchObjWProperty(candidateList[i]['id'], 'P17')
        if(len(results['results']['bindings']) > 0):
            if(results['results']['bindings'][0]['itemLabel']['value'] == 'Indonesia'):
                scoreList[i] = scoreList[i] + 1
        
        lblDis = lDistance(goal, candidateList[i]['label'].lower())
        aliDis = 10000000
        if('aliases' in candidateList[i]):
            aliDis = lDistance(goal, candidateList[i]['aliases'][0].lower())
        
        scoreList[i] = scoreList[i] - min(lblDis, aliDis)
    
    maxScore = max(scoreList)
    if(maxScore < threshold):
        return ''

    idx = scoreList.index(maxScore)
    return candidateList[idx]['id']

def searchID(flag, cell, rowHead,limit=5):
    json = searchEntity(cell.lower(), limit)['search']
    id = ''
    if(len(json) > 1):
        id = ranking(json, cell.lower(), flag, rowHead)
    elif(len(json) == 1):
        id = json[0]['id']
    
    if(id == '' and flag):
        id = 'QNew'
    elif(id == ''):
        id = 'QNPNew'
        
    return id

def isCordinatLike(col):
    kordinatLike = ['koordinat','kordinat','latitude','longitude','latitude','bujur','lintang']
    for x in str(col).split(" "):
        print("[DEBUG-KordinatLike] kata : {} , Kata in KordinatLike {}".format(x,x in kordinatLike))
        if x in kordinatLike:
            return True
    
    return False

    
def makeDatatypeIndex(df, entityColumn):
    dtMap = []
    header_list = df.columns
    for elem in header_list:
        if elem in entityColumn:
            dtMap.append(0)
        else:
            dtMap.append(1)
    return dtMap

def makeDatatypeMap(header_list, df):
    num_of_row = df.shape[0]
    rr0=0
    rr1=int(num_of_row/2)
    rr2=num_of_row-1
    reference_row0 = [str(x) for x in list(df.loc[rr0, header_list])]
    reference_row1 = [str(x) for x in list(df.loc[rr1, header_list])]
    reference_row2 = [str(x) for x in list(df.loc[rr2, header_list])]
    ref_rows=[reference_row0,reference_row1,reference_row2]
    print("[DEBUG] dttyemap rr indx : {}-{}-{}".format(rr0,rr1,rr2))
    print(list(df.loc[rr1, header_list]))
    dtMap = []
    dtColTypes = {}
    for reference_row in ref_rows:
        index = 0
        print("+====================== {} ==========".format(reference_row))
        for elem in reference_row:
            print("+?????????====================== {} ==========".format(elem))
            dtColType=""
            pattern_quantity = re.compile("[-+.,()0-9]+")
            pattern_float = re.compile("[0-9\.-]+")
            pattern_globe = re.compile("^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)$")
    #         pattern_web = re.compile("[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)")
            pattern_web = re.compile("^[a-zA-Z0-9_\-\@]+\.[a-zA-Z0-9]_\-\.")
            pattern_literal = re.compile("[\.\,\!\?\>\<\/\\\)\(\-\_\+\=\*\&\^\%\$\#\@\!\:\;\~]")
            pattern_time = re.compile("^([0-2][0-9]|(3)[0-1])([\/,-])(((0)[0-9])|((1)[0-2]))([\/,-])\d{4}$")
            is_quantity = pattern_quantity.match(elem)
            if is_quantity:
                is_float = pattern_float.match(elem)
                is_time = pattern_time.match(elem)
                is_kordinatLike = isCordinatLike(header_list[reference_row.index(elem)])
                if is_time:
                     dtColType="Time"
                elif pattern_globe.match(elem):
                     dtColType="GlobeCoordinate"
                elif is_float and isCordinatLike(header_list[reference_row.index(elem)]):
                    dtColType="GlobeCoordinate"
                else:
                    try:
                        x = float(elem)
                        dtColType="Quantity"
                    except ValueError:
                        dtColType="String"
            else:
                is_literal_string = bool(pattern_literal.search(elem))
                is_url_string = bool(pattern_literal.match(elem))
                print("[DEBUG] is_literal {} == {}".format(elem,is_literal_string))
                if is_url_string:
                    dtColType="URL"
                elif is_literal_string:
                    dtColType="String"
                else :
                    dtMap.append(header_list[reference_row.index(elem)])
                    dtColType="WikibaseItem"

            if header_list[index] in dtColTypes:
                dtColTypes[header_list[index]].append(dtColType)
            else:
                dtColTypes[header_list[index]] = [dtColType]
            index=index+1

    print("[DEBUG] DtColTypes ON MakeDtType \n == {}".format(dtColTypes))
    for key, value in dtColTypes.items():
        value_score = {}
        max_score = 0
        max_dt = ""
        for x in value:
            if x in value_score:
                value_score[x]=value_score[x]+1
            else :
                value_score[x] = 1
            if value_score[x] > max_score:
                max_score = value_score[x]
                max_dt = x
        dtColTypes[key]=max_dt
        if max_dt == 'WikibaseItem':
            dtMap.append(key)     
    return dtMap, dtColTypes


def lDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

#jalan
def check_protagonist(df):
    ranking = {}
    for col in df.columns:
        entities = set()
        for index, row in df.iterrows():
            if isinstance(row[col],str):
                entities.add(str(row[col]))
                print("[DEBUG] protagonist, row[col] string : {}".format(row[col]))
            else:
                entities.add(str(row[col].values[0]))
        ranking[col] = len(entities)
    return ranking

def give_verdict_base(df_entity, ranking_diversity):
    ranking = {}
    maxValue = -1
    maxColumn = ""
    for key, value in ranking_diversity.items():
        score = value + len(df_entity.columns)-list(df_entity.columns).index(key)
        if maxValue < score:
            maxValue = score
            maxColumn = key
        ranking[key] = score
    return maxColumn, maxValue, ranking

def give_verdict_normalized(df_entity, ranking_diversity, weightDiverse=0.5, weightColumnOrder=0.5):
    df_length = df_entity.shape[0]
    ranking = {}
    maxValue = -1
    maxColumn = ""
    for key, value in ranking_diversity.items():
        diverseScore = value/df_length
        columnOrderScore = 1 - (list(df_entity.columns).index(key)/len(df_entity.columns))
        score = (weightDiverse * diverseScore) + (weightColumnOrder * columnOrderScore)
        if maxValue < score:
            maxValue = score
            maxColumn = key
        ranking[key] = score
    return maxColumn, maxValue, ranking

#tie breaker on highest value . but the highest value has multiplice instances
def give_verdict_columntb(df_entity, ranking_diversity):
    df_length = df_entity.shape[0]
    ranking = {}
    maxValue = -1 #value can not be lower or equal to zero , so this is safe initial poin
    maxColumns = []
    for key, value in ranking_diversity.items():
        if value > maxValue:
            maxColumns=[key]
            maxValue = value
        elif value == maxValue:
            maxColumns.append(key)
        else:
            pass
        ranking[key] = value

    if len(maxColumns) > 1:
        maxOrderScore = -1  #value can not be lower or equal to zero , so this is safe initial poin
        for col in maxColumns:
            columnOrderScore = 1 - (list(df_entity.columns).index(key)/len(df_entity.columns))
            if columnOrderScore > maxOrderScore:
                maxColumns[0] = col
                maxOrderScore = columnOrderScore
            ranking[col] = ranking[col]+columnOrderScore
    print("[DEBUG] Ranking Diversity : {}".format(ranking_diversity))
    return maxColumns[0], maxValue, ranking

#tie breaker on , if any, highest value that have multiplie instances ( So it could be , not the highest value , but highest value that has multiple instances)

#tie breaker on any multiple instances


#entropy
def give_verdict_entropy(df_entity):
    maxEntropy = -1
    maxColumn=""
    ranking={}
    for col in df_entity.columns:
        dummy, counts = np.unique(df_entity[col].astype(str), return_counts=True)
        probs = []
        numbers_of_data=df_entity.shape[0]
        for occ in counts:
            probs.append(occ/numbers_of_data)
        entropy = scipy.stats.entropy(probs)#base = e
        if entropy > maxEntropy:
            maxEntropy=entropy
            maxColumn=col
        ranking[col]=entropy
    return maxColumn, maxEntropy, ranking

# Jalan MAIN
def determine_protagonist(df, dtMap):
    entity_columns = dtMap
    df_entity = df[entity_columns]
    ranking = check_protagonist(df_entity)
    hasil={}
    hasil['base'], score, info = give_verdict_base(df_entity, ranking)
    hasil['normalize-0.5:0.5'], score, info = give_verdict_normalized(df_entity, ranking)
    hasil['normalize-0.7:0.3'], score, info = give_verdict_normalized(df_entity, ranking, 0.7, 0.3)
    hasil['normalize-0.3:0.7'], score, info = give_verdict_normalized(df_entity, ranking, 0.3, 0.7)
    hasil['base-columntb'], score, info = give_verdict_columntb(df_entity, ranking)
    hasil['entropy'], score, info = give_verdict_entropy(df_entity)



    return hasil

def check_wb_type(property_id):
    if len(property_id) <= 1 or property_id[0] != 'P':
        return ''
    res = searchPropertyRange(property_id)
    wd_type = res['results']['bindings'][0]['wbtype']['value']
    return wd_type[wd_type.find('#')+1:]

def identify_literal_columns(df):
    literal_columns = []
    samplerow = df.shape[0]
    a = df.loc[0:samplerow,:]
    for col in a.columns:
        isLiteral = False
        for index, row in a.iterrows():
            pattern = re.compile("^Q([1-9]+)")#match the Q123123 pattern of entity name
            
            if pattern.match(str(row[col])):
                continue
            elif str(row[col]) == "QNPNew" or str(row[col]) == "QNew":
                continue
            else:
                isLiteral = True
        if isLiteral and col != protagonist:
            literal_columns.append(col)
    return literal_columns
    
def identify_double_columns(df):
    double_columns = {}
    columns = df.columns
    for col in columns:
        if "(" in col:
            print("[DEBUG] Double Col "+col + " " + col[:col.find("(")])
            double_columns[col] = col[:col.find("(")]
    return double_columns

def format_qs_df(df_qs, literal_columns):
    print("[QS FORMATTING] Checking property range")
    for liter_col in list(set(literal_columns)):
        if liter_col in df_qs.columns:
            print("[QS FORMATTING] checking for {}".format(liter_col))
            range_type = check_wb_type(liter_col)
            print(range_type)
            if range_type == 'String':
                df_qs[liter_col]="\"\"\"\"" + df_qs[liter_col] + "\""
            elif range_type == 'Time':
                df_qs[liter_col]="+" + df_qs[liter_col] + "T00:00:00Z/9"
            elif range_type == 'Monolingualtext':
                df_qs[liter_col]="id:\"" + df_qs[liter_col] + "\""
            elif range_type == 'GlobeCoordinate':
                temp = df_qs[liter_col]
                if len(temp.shape) > 1 and temp.shape[1] > 1:
                    col1 = temp.iloc[:,0]
                    col2 = temp.iloc[:,1]
                    temp_col = "@"+col1.apply(str) + "/"+col2.apply(str)
                    df_qs.drop(columns=[liter_col], inplace=True)
                    df_qs[liter_col]=temp_col
                elif len(temp.shape) == 1 or (len(temp.shape) > 1 and temp.shape[1] == 1) :
                    temp = ["@"+x.replace(",","/").replace(" ","") for x in temp]
                    df_qs[liter_col]=temp
    print("END checking property range")
    return df_qs

def map_property_api(columns, dttype, parentApiURL="http://od2wd.id/api/"):
    properties = []
    parent_api_link=parentApiURL
    for col in columns:
        obj = {}
        obj['item'] = col
        obj['item_range'] = dttype[col]
        obj['limit'] = 5
        properties.append(obj)
    payload = {}
    payload['properties']=properties
    # payload = json.dumps(payload)
    print(payload)
    print("[PHASE-2], Calling Url for Property Mapping")
    url = "{}/main/property".format(parent_api_link)
    response = requests.post(url, json=payload)
    
    json_data = json.loads(response.text)
    result = {}
    result_label = {}
    print(json_data)
    for obj in json_data['results']:
        if len(obj['map_to']) > 0:
            result[str(obj['item'])] = obj['map_to'][0]['id']
            result_label[str(obj['item'])] = obj['map_to'][0]['label']
        else:
            result[str(obj['item'])] = ''
            result_label[str(obj['item'])] = ''
    return result, result_label

def map_protagonist_api(protagonist, parentApiURL="http://od2wd.id/api/"):
    url="{}/main/protagonist".format(parentApiURL)
    payload = {}
    payload['item'] = protagonist
    payload['limit'] = 10
    response = requests.post(url, json=payload)
    print(response.text)
     
    json_data = json.loads(response.text)
    # for obj in json_data['results']:
    result = ''
    result_label = 'Padanan Tidak Ditemukan'
    result_description = ''
    if len(json_data['results']) > 0:
        result = json_data['results'][0]['id']
        result_label = json_data['results'][0]['label']
        result_description = json_data['results'][0]['description']

    return result, result_label, result_description

def qs_add_instance_of(df, procId, protagonist):
    mapping = var_settings.mapping_dict[procId]
    if protagonist not in mapping:
        return df, False
    protagonistMapping = mapping[protagonist]
    pMapExist = len(protagonistMapping) > 1 
    if pMapExist:
        df['P31']=protagonistMapping
    return df, pMapExist