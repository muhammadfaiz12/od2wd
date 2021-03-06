from src.mapper import mapProperty, mpRankWTypeSim
import csv
import shelve
import pandas as pd
from src.main_utils import get_label_from_map_file
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

def get_ner_context(title:str):
    url = "{}/main/ner".format(var_settings.parent_api_link)
    raw_response = requests.get(url, params={"title":title})
    response = json.loads(raw_response.text)
    if raw_response.status_code == 200 and 'results' in response:
        return response['results']
    return []


def searchID(flag, cell, rowHead, context=[], limit=3):
    # json = searchEntity(cell.lower(), limit)['search']
    responseCode, id = link_entity_api(cell, rowHead, context, limit) 
    print(cell)
    print(responseCode)
    print(id)
    not_found = id == '' or id =='NOTFOUND'
    if(not_found and flag):
        id = 'QNew'
    elif(not_found):
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
            if range_type == 'String' or range_type =='ExternalId' :
                df_qs[liter_col]="\"" + df_qs[liter_col] + "\""
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

def link_entity_api(item: str, headerValue: str, context=[], limit=3):
    payload = {}
    body ={}
    payload['item']=item
    payload['headerValue']=headerValue
    payload['contexts']= [x for x in context if len(x) > 0]
    payload['limit']=limit
    body['entities']=[payload]
    print("[PHASE-2], Calling Url for Entity Linking")
    url = "{}/main/entity".format(var_settings.parent_api_link)
    response = requests.post(url, json=body)
    if response.status_code != 200:
        return response.status_code, ''
    #Formatting to extract qid from response, because api response cannot be easily parsed
    #think of this as
    #qid = response['results'][0]["item"][0]["id"]
    response_body = json.loads(response.text)
    qid = response_body['results'][0]["item"]
    qid = qid.replace("{","").replace("}","").split(",")[0].split(":")[1].replace("'","").replace(" ","")
    return response.status_code, qid

def map_protagonist_api(protagonist, parentApiURL="https://od2wd.id/api/"):
    url="{}/main/protagonist".format(parentApiURL)
    payload = {}
    payload['item'] = protagonist
    payload['limit'] = 10
    response = requests.get(url, params=payload)
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
    if protagonist not in mapping or "NOTFOUND" in mapping[protagonist]:
        return df, False
    protagonistMapping = mapping[protagonist]
    pMapExist = len(protagonistMapping) > 1 
    if pMapExist:
        df['P31']=protagonistMapping
    return df, pMapExist

#col is original column name
def getColumnName(procId, col, step):
    colName = ""
    try:
        with shelve.open("db/col-db") as s:
            colName=s[procId]['column'][col][step]
            print("{}-{}".format(colName, step))
            if step == 'results' and "(" in colName:
                occ_num = int(colName[colName.find("(")+1:].replace(")",""))
                occ_num-=1
                colName=colName[:colName.find("(")]+".{}".format(occ_num)
    except Exception as e:
        print("EXCEPTION on Removing Inaccurate colum \n {} \n ==== END ===".format(str(e.with_traceback)))
    return colName

#Dropping P31
def dropP31(procId, df_m, df_r):
    df_m.columns = [x[:x.find('-')]+"-[Protagonist-Column]" if "[Protagonist]" in x else x for x in df_m.columns]
    #dropping P31 and its accompanying source column
    source = []
    if "url" in var_settings.job_metadata_dict[procId].keys():
        source = [df_r.columns[list(df_r.columns).index("P31")+1]]
    df_r.drop(["P31"]+source, inplace=True, axis=1)

    df_r.to_csv("data/results/{}".format(procId), index=False)
    df_m.to_csv("data/mapped/{}".format(procId), index=False)
    return

def checkProtagonist(procId):
    protagonist = ""
    try:
        with shelve.open("db/col-db") as s:
            protagonist=s[procId]['protagonist-column']
    except Exception as e:
        print("EXCEPTION on checking protagonist colum \n {} \n ==== END ===".format(str(e)))
    return protagonist

def get_column_dict(procId):
    colName = ""
    try:
        with shelve.open("db/col-db") as s:
            return s[procId]['column']
    except Exception as e:
        print("EXCEPTION on Getting Column Dict \n {} \n ==== END ===".format(str(e.with_traceback)))

def checkMergedColumn(procId, del_m, del_l, del_r):
    isMerge = False
    #check merged column
    mergedColumn = "P625" #latitude/longitude into 1 column
    for col in del_r:
        if col is not None and mergedColumn in col:
            isMerge = True
    if isMerge:
            with shelve.open("db/col-db") as s:
                for col in s[procId]['column'].keys():
                    if s[procId]['column'][col]['results'] is not None and mergedColumn in s[procId]['column'][col]['results'] and s[procId]['column'][col]['mapped'] not in del_m:
                        del_m.append(s[procId]['column'][col]['mapped'])
                        del_l.append(s[procId]['column'][col]['linked'])
           # print("EXCEPTION on checking merged colum \n {} \n ==== END ===".format(e))
    return del_m, del_l, del_r

def drop_export_column(procId, stayColumns):
    mapping = get_label_from_map_file(procId)
    delColumns = [x for x in mapping.keys() if x not in stayColumns]

    df_r = load_data(procId, "results")
    df_m = load_data(procId, "mapped")
    df_l = load_data(procId, "linked")
    protagonist = checkProtagonist(procId)
    if protagonist in delColumns: 
        #check if p31 exists
        if "P31" in df_r.columns:
            dropP31(procId, df_m, df_r)
        delColumns.remove(protagonist)

    if len(delColumns) < 1:
        return
    print("WAHAHA")
    print(delColumns)
    delColumns_m = []
    delColumns_l = []
    delColumns_r = []

    print(len(delColumns_m))
    delColumns_m = [getColumnName(procId, x, 'mapped') for x in delColumns if x is not None]
    delColumns_l = [getColumnName(procId, x, 'linked') for x in delColumns if x is not None]
    delColumns_r = [getColumnName(procId, x, 'results') for x in delColumns if x is not None]

    delColumns_m, delColumns_l, delColumns_r = checkMergedColumn(procId, delColumns_m, delColumns_l, delColumns_r)
    delColumns_m, delColumns_l, delColumns_r = [x for x in delColumns_m if x is not None], [x for x in delColumns_l if x is not None], [x for x in delColumns_r if x is not None]

    #Adding accomapnying source columns to be dropped(if exitst)
    if "url" in var_settings.job_metadata_dict[procId].keys():
        delColumns_r = delColumns_r + [df_r.columns[list(df_r.columns).index(x)+1] for x in delColumns_r]
    print(delColumns_m)
    print(delColumns_r)
    print(delColumns_l)
    df_r.drop(delColumns_r, inplace=True, axis=1)
    df_m.drop(delColumns_m, inplace=True, axis=1)
    df_l.drop(delColumns_l, inplace=True, axis=1)
    
    print(len(delColumns_m))
    print("[LOG] Dropping column {} on {}".format(delColumns, procId))

    df_m.to_csv("data/mapped/{}".format(procId), index=False)
    df_l.to_csv("data/linked/{}".format(procId), index=False)

    temp_col = []
    for col in df_r.columns:
        if "." in col:
            col=col[:col.find(".")]
        temp_col.append(col)
    df_r.columns=temp_col

    df_r.to_csv("data/results/{}".format(procId), index=False)

    return

def format_metadata_job_detail(protagonist:str, metadata: dict) -> str:
    stringified_tags, title, url, description = "", "", "", ""
    if "tags" in metadata.keys():
        #Result format is based on FE Designer's request
        stringified_tags = str(metadata["tags"]).replace("[","").replace("]","")
    if "title" in metadata.keys():
        title = str(metadata["title"])
    if "url" in metadata.keys():
        url = str(metadata["url"])
    if "description" in metadata.keys():
        description = str(metadata["description"])
    result = "<div><a>Title</a><p>{}</p><a>Protagonist Column</a><p>{}</p><a>URL</a><p>{}</p><a>Tags</a><p>{}</p><a>Description</a><p>{}</p></div>".format(protagonist, title, url, stringified_tags, description)
    return result

def get_result_csv_text(procId: str) -> str:
    try:
        with open("data/results/{}".format(procId)) as csv_file:
            result = csv_file.read()
            return result
    except Exception as e:
            print("Error on getting clipboard \n {} \n ".format(e.with_traceback))
            return ""

def get_label_of_linked_df(df_l, df_m, columns: dict):
    pattern = re.compile("(Q[1-9])\w+")
    entity_col = []
    entity_col_pair = {}

    #identify entity column
    for l_col in df_l.columns:
        print(str(df_l[l_col][0]))
        if bool(pattern.match(str(df_l[l_col][0]))):
            entity_col.append(l_col)

    #loop e col
    for ec in entity_col:
        for col in columns.keys():
            #getting mapped label of the linked
            if columns[col]['linked'] == ec:
                entity_col_pair[ec] = columns[col]['mapped']

    #mash old label with link result
    df_result = df_l.copy()
    print(df_l.columns)
    print(entity_col_pair.keys())
    print(df_m.columns)
    for ec in entity_col:
        #Skipping P31 because its auto generated column, hence no old label
        if ec == "P31":
            continue
        df_result[ec] = df_m[entity_col_pair[ec]]+" - "+df_l[ec]
    
    #Add protagonist column label
    protagonist_col_l = "qid"
    
    protagonist_col_m = df_m.columns[0]
    for col_m in df_m.columns:
        if "[Protagonist]" in col_m:
            protagonist_col_m=col_m

    print(protagonist_col_l)
    print(protagonist_col_m)
    print(df_result.columns)
    df_result[protagonist_col_l] = df_m[protagonist_col_m]+" - "+df_l[protagonist_col_l]

    return df_result
