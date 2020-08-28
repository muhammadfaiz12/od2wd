
# coding: utf-8

# In[1]:


from mapper import mapProperty, mpRankWTypeSim
import csv
import pandas as pd
from wikimedia import searchEntity, searchObjWProperty, searchProperty, searchPropertyRange
from dateutil.parser import parse
import operator
import re
import numpy as np
import sys, os
import scipy.stats 
from dateutil.parser import parse


# In[24]:


#GIBRAN THINGS
limit = 5
threshold = 0

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False
    
def ranking(candidateList, goal, flag, propertyLbl):
    scoreList = [0] * len(candidateList)
    for i in range(len(candidateList)):
#         if(not flag):
#             results = searchObjWProperty(candidateList[i]['id'], 'P31')
#             if(len(results['results']['bindings']) > 0):
#                 temp = False
#                 for elem in results['results']['bindings']:
#                     if(elem['itemLabel']['value'].lower() == propertyLbl.lower()):
#                         temp = True
#                         break
#                 if(not temp):
#                     scoreList[i] = scoreList[i] - 5
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

def searchID(is_protagonist, cell, rowHead):
    json = searchEntity(cell.lower(), limit)['search']
    id = ''
    if(len(json) > 1):
        id = ranking(json, cell.lower(), is_protagonist, rowHead)
    elif(len(json) == 1):
        id = json[0]['id']

    not_found = id == '' or "NOTFOUND" in id
    if(not_found and is_protagonist):
        id = 'QNew'
    elif(not_found):
        id = 'QNPNew'
        
    return id

def isCordinatLike(col):
    kordinatLike = ['koordinat','kordinat','latitude','longitude','latitude']
    for x in str(col).split(" "):
        print("kata : {} , Kata in KordinatLike {}".format(x,x in kordinatLike))
        if x in kordinatLike:
            return True
    
    return False

    
def makeDatatypeIndex(header_list, df):
    dtMap = []
    for elem in df.loc[0, header_list]:
        try:
            if(elem.replace('.','').replace(',', '').replace('-', '').replace(' ', '').isdigit()):
                dtMap.append(1)
            elif('jl.' in elem.lower()):
                dtMap.append(1)
            elif(is_date(elem)):
                dtMap.append(1)
            else:
                dtMap.append(0)
        except AttributeError:
            dtMap.append(1)
    return dtMap

def makeDatatypeMap(header_list, df):
    reference_row = [str(x) for x in list(df.loc[0, header_list])]
    dtMap = []
    dtColTypes = {}
    index=0
    for elem in reference_row:
        dtColType=""
        pattern_quantity = re.compile("[-+.,()0-9]+")
        pattern_float = re.compile("[0-9\.-]+")
        pattern_globe = re.compile("^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$")
#         pattern_web = re.compile("[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)")
        pattern_web = re.compile("^[a-zA-Z0-9_\-\@]+\.[a-zA-Z0-9_\-\.")
        pattern_literal = re.compile("[\.\,\!\?\>\<\/\\\)\(\-\_\+\=\*\&\^\%\$\#\@\!\:\;\~]")
        is_quantity = pattern_quantity.search(elem)
        print("Elem : {} , is_quantity : {}, is_date: {}".format(elem,bool(is_quantity),is_date(elem)))
#         print(list(df.loc[0, header_list]))
        if is_quantity:
            is_float = pattern_float.match(elem)
            is_kordinatLike = isCordinatLike(header_list[reference_row.index(elem)])
            print( is_float)
            if not is_float and is_date(elem):
                 dtColType="Time"
            elif pattern_globe.match(elem):
                 dtColType="GeolocationCoordinate"
            elif is_float and isCordinatLike(header_list[reference_row.index(elem)]):
                dtColType="GeolocationCoordinate"
            else:
                try:
                    x = float(elem)
                    dtColType="Quantity"
                except ValueError:
                    dtColType="String"
        else:
            is_literal_string = bool(pattern_literal.match(elem))
            is_url_string = bool(pattern_literal.match(elem))

            if is_url_string:
                dtColType="URL"
            elif is_literal_string:
                dtColType="String"
            else :
                dtColType="WikibaseItem"

        dtColTypes[header_list[index]]=dtColType 
        index=index+1
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
            entities.add(row[col])
        ranking[col] = len(entities)
    return ranking

def give_verdict_base(df_entity, ranking_diversity):
    ranking = {}
    maxValue = -1
    maxColumn = ""
    for key, value in ranking_diversity.items():
        score = value + len(df_entity.columns)-list(df_entity.columns).index(key)
        if maxValue <= score:
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
        if maxValue <= score:
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
#         print(str(type(entropy))+ " " + str(maxEntropy))
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
#     for keys, value in hasil.items():
#         print(str(keys) + " : " + str(value))

def check_wb_type(property_id):
    if len(property_id) <= 1 or property_id[0] != 'P':
        return ''
    res = searchPropertyRange(property_id)
    wd_type = res['results']['bindings'][0]['wbtype']['value']
    return wd_type[wd_type.find('#')+1:]


# In[23]:


os.listdir("data/dataKicut/")


# In[3]:


nama_folder = "data/dataKicut/"
nama_csv = "daftar-taman-kota-bandung.csv"
nama_file = nama_folder + nama_csv
df = pd.read_csv(nama_file, encoding='latin-1')
df_asli_column_asli = df.columns
df


# In[4]:


header_list = [x.replace("_"," ").lower() for x in list(df.columns)]
df.columns=header_list
if 'no.' in header_list:
    header_list.remove('no.')
# header_list=[x.lower() for x in header_list]
header_list


# In[25]:


dtMap, dt_type = makeDatatypeMap(header_list, df)
dt_type


# In[16]:


hasil_verdict = determine_protagonist(df, dtMap)
protagonist = hasil_verdict['entropy']
protagonist


# In[17]:


dt_type.pop(protagonist)
header_list.remove(protagonist)
types_list = []
for head in header_list:
    types_list.append(dt_type[head])
mapping, mappingLabel = mpRankWTypeSim(header_list, types_list)
mapping[protagonist]=protagonist
header_list.append(protagonist)
mapping


# In[18]:


header_list


# In[19]:


# header_list.remove(protagonist)
# mapping,xa = mapProperty(header_list, '')
# mapping[protagonist] = protagonist
# header_list.append(protagonist)
# xa


# In[20]:


dtMap = makeDatatypeIndex(header_list, df)
dtMap
# header_list


# In[21]:


convertMap = {} 
finalMap = {} 
print("Start processing Table") 
counter = 2 
for header in header_list: 
    if(header in mapping): 
        print("Processing {} Column".format(header)) 
        columnList = [] 
        for cell in df[header]: 
            if(dtMap[header_list.index(header)]): 
                id = cell 
            else: 
                temp = "{}{}".format(header, cell) 
                if(temp in convertMap): 
                    id = convertMap[temp] 
                else: 
                    id = searchID(protagonist == header, str(cell), header) 
                    convertMap[temp] = id 
            columnList.append(id) 
        print("finished processing {} datas".format(len(columnList))) 
        if(header == protagonist): 
            finalMap[header] = columnList 
        else: 
            if(mapping[header] in finalMap): 
                finalMap['{}({})'.format(mapping[header], counter)] = columnList 
                counter = counter + 1 
            else: 
                finalMap[mapping[header]] = columnList 

print("All task Finished")


# In[23]:


new_df = pd.DataFrame.from_dict(finalMap)
new_df
# convertMap


# In[24]:


new_df.to_csv('data/dummymapping.csv')


# In[33]:


df_asli


# In[36]:


df_asli = df
df = pd.read_csv("data/dummymapping.csv")
protagonist = protagonist
df.head()


# In[37]:


def identify_literal_columns(df):
    literal_columns = []
    samplerow = df.shape[0]
    a = df.loc[0:samplerow,:]
    for col in a.columns:
        isLiteral = False
        for index, row in a.iterrows():
#             print("==========> " + row[[col]])
            pattern = re.compile("^Q([1-9]+)")#match the Q123123 pattern of entity name
            
            if pattern.match(str(row[col])):
                continue
            elif str(row[col]) == "QNPNew" or str(row[col]) == "QNew":
                continue
            else:
                isLiteral = True
        if isLiteral and col != protagonist:
#             print(col)
            literal_columns.append(col)
    return literal_columns
    
def identify_double_columns(df):
    double_columns = {}
    columns = df.columns
    for col in columns:
        if "(" in col:
            print(col + " " + col[:col.find("(")])
            double_columns[col] = col[:col.find("(")]
    return double_columns


# In[53]:


df_qs = pd.DataFrame(df)
df_qs=df_qs.loc[:, ~df_qs.columns.str.contains('^Unnamed')] #drop unnamed col (index)
df_qs


# In[54]:


# [CAREFULL]
# # CELL TO ADD MANUALLY ADDED PROPERTY

# df_qs.columns = [x if x!='(3)' else 'P625' for x in df_qs.columns]


# In[55]:



literal_columns = identify_literal_columns(df_qs)
double_columns = identify_double_columns(df_qs)
df_qs.rename({protagonist:'qid'}, axis=1, inplace=True)

# print(df_qs.columns[0])
#ngereplace QID(protagonist) yg sifat Qnew
df_qs.replace(["QNew","QNPNew"],"",inplace=True)

df_qs.columns=[c if c not in double_columns.keys() else double_columns[c] for c in df_qs.columns]

print(literal_columns)
#nambain label dari csv asli sama nambain quote untuk literal columns
df_qs['Lid']=df_asli[protagonist]



print("START checking property range")
for liter_col in literal_columns:
    print("checking for {}".format(liter_col))
    range_type = check_wb_type(liter_col)
#      if dt_type[mapping[liter_col]] == 'String':
    #  buat mbedain keluarga besar string
    if range_type == 'String':
        df_qs[liter_col]="\"\"\"\"" + df_qs[liter_col] + "\""
    elif range_type == 'Monolingualtext':
        df_qs[liter_col]="id:\"" + df_qs[liter_col] + "\""
    elif range_type == 'GlobeCoordinate':
        temp = list(df_qs[liter_col])
        temp = ["@"+x.replace(",","/").replace(" ","") for x in temp]
        df_qs[liter_col]=temp
        
print("END checking property range")
  
#     pattern = re.compile("^-?[0-9][0-9,\.]+$")
#     pattern = re.compile(".*[a-zA-Z].*")

#pemindahan QID ke depan
df_qs=df_qs[['qid'] + [c for c in df_qs if c != 'qid']]


# In[56]:


df_qs.head()


# In[57]:


# # [CAREFULL]
# # CELL TO ADD MANUALLY ADDED PROPERTY
# df_qs.columns = list(df_qs.columns).replace('',)
df_qs.head()


# In[58]:


df_qs.to_csv('data/result/qs_file_result-{}.csv'.format(nama_csv), index=False)


# In[ ]:


import os 
os.remove("data/quickstatements_file.csv") 
print("File Removed!")

