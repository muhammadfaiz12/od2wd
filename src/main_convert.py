from src.utils import *
import pandas as pd
import var_settings

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

def link_data(df, protagonist,entity_column,mapping):
    dtMap = makeDatatypeIndex(df,entity_column)
    header_list=list(df.columns)
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
def generate_qs(df_map,df_asli,protagonist,literal_columns_label,procId):
    df_qs = pd.DataFrame(df_map)
    df_qs = df_qs.loc[:, ~df_qs.columns.str.contains('^Unnamed')] #drop unnamed col (index)
    for col in df_qs.columns:
        #drop any row that has unlinkable property
        df_qs = df_qs[~df_qs[col].astype(str).str.contains("QNPNew")]

    double_columns = identify_double_columns(df_qs)
    df_qs.rename({protagonist:'qid'}, axis=1, inplace=True)

    #ngereplace QID(protagonist) yg sifat Qnew
    df_qs.replace(["QNew"],"",inplace=True)
    df_qs.columns=[c if c not in double_columns else double_columns[c] for c in df_qs.columns]

    #nambain label dari csv asli sama nambain quote untuk literal columns
    df_qs['Lid']=df_asli[protagonist]

    literal_columns = []
    for x in literal_columns_label:
        if x in var_settings.mapping_dict[procId]:
            literal_columns.append(var_settings.mapping_dict[procId][x])
     
    print("LITERAL COLUMN : {}".format(literal_columns))

    df_final = format_qs_df(df_qs,literal_columns)
    valid_column = [x for x in list(df_final.columns) if len(x) >= 1 ]
    df_final = df_final[['qid'] + [c for c in list(set(valid_column)) if c != 'qid']]
    #mindain qid ke depan
    print(df_final.columns)
    # df_final.to_csv('data/results/{}'.format("-debug"))
    return df_final

def check_result(nama_file):
    return os.path.isfile('data/results/{}'.format(nama_file))   
