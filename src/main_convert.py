from src.utils import *
import pandas as pd

def main_convert():
    pass

def load_data(nama_file):
    df = pd.read_csv("data/uncleaned/{}".format(nama_file), encoding='latin-1')
    df_asli_column_asli = df.columns
    return df, df_asli_column_asli

def preprocess_data(file_name):
    df = pd.read_csv("data/uncleaned/{}".format(file_name), encoding='latin-1')
    header_list = [x.replace("_"," ").lower() for x in list(df.columns)]
    df.columns=header_list
    if 'no.' in header_list:
        header_list.remove('no.')
    
    dtMap, dt_type = makeDatatypeMap(header_list, df)
    print(dtMap)
    hasil_verdict = determine_protagonist(df, dtMap)
    protagonist = hasil_verdict['base-columntb']
    df.to_csv('data/processed/'+file_name)
    return df,dtMap, dt_type,protagonist,header_list


def map_data(df,dt_type,protagonist,header_list):
    dt_type.pop(protagonist)
    header_list.remove(protagonist)
    types_list = []
    for head in header_list:
        types_list.append(dt_type[head])
    mapping, mappingLabel = mpRankWTypeSim(header_list, types_list)
    mapping[protagonist]=protagonist
    header_list.append(protagonist)
    return mapping

def link_data():
    dtMap = makeDatatypeIndex(header_list, df)
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
    return finalMap
def publish_data():
    pass