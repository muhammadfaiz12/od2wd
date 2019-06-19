import os
import platform
import requests, json, wget
import pandas as pd
from datetime import datetime

def get_catalogue():
    listOfFile = os.listdir('data/uncleaned/')
    date_map = {}
    res = []
    res_time = []
    time = None
    for f in listOfFile:
        path_to_file='data/uncleaned/'+f
        if platform.system() == 'Windows':
            time = os.path.getctime(path_to_file)
        else:
            stat = os.stat(path_to_file)
            try:
                time = stat.st_birthtime
            except AttributeError:
                # Linux Probably 
                time = stat.st_mtime
        time = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
        res_time.append(time)
        if time in date_map:
            date_map[time] = date_map[time].append(f)
        else:
            date_map[time] = [f]
    res_time = sorted(res_time, reverse=True)
    for time in res_time:
        for f in date_map[time]:
            res.append(f)
    return res, res_time

def check_file_name(nama_file):
    fix_name=nama_file
    idx = 2
    status = os.path.isfile('data/uncleaned/{}'.format(nama_file))
    print("[PHASE-1] Checking old file with same name exist {}".format(str(status)))
    if status:
        while os.path.isfile('data/uncleaned/{}'.format(fix_name)):
            fix_name= "{}-{}".format(str(idx),nama_file)
            idx = idx + 1
        print("[PHASE-1] Renaming File to {}".format(fix_name))
        return fix_name
    else:
        return fix_name

def check_result_finished(nama_file):
    status = os.path.isfile('data/results/{}'.format(nama_file))
    if status:
        return True, pd.read_csv("data/results/{}".format(nama_file), encoding='latin-1')
    else:
        return False, None

def save_mapping_result(df, procId, mapping):
    mapped_columns = []
    for col in df.columns:
        try:
            mapped_columns.append("{}-{}".format(str(col),mapping[col]))
        except KeyError:
            mapped_columns.append("padanan tidak ditemukan")
    df.columns = mapped_columns
    df.to_csv("data/mapped/{}".format(procId), index=False)
    return

def save_linking_result(df, procId):
    df.to_csv("data/linked/{}".format(procId), index=False)
    return

def get_job_status(procId):
    result = []
    states = ['uncleaned', 'processed', 'mapped', 'linked', 'results']
    for state in states:
        status = os.path.isfile('data/{}/{}'.format(state, procId))
        result.append(status)
    return result

def get_label_from_map_file(procId):
    try:
        df = pd.read_csv("data/mapped/{}".format(procId), encoding='latin-1')
        result = {}
        for col in df.columns:
            temp =  str(col).split('-')
            label=''
            for x in range(1,len(temp)):
                label+="-"+str(temp[x])
            result[temp[0]]=label[1:]
        return result
    except:
        result = {}
        return result

def get_publish_qs_url(procId):
    filename="data/results/{}".format(procId)
    csv = ''
    with open(filename) as f:
        csv = f.read()
    csv=csv.replace('\n',"%0A")
    csv=csv.replace('\"',"%22")
    csv=csv.replace(' ', "%20")

    url="https://tools.wmflabs.org/quickstatements/api.php"
    payload = {}
    payload['action'] = 'import'
    payload['format'] = 'csv'
    payload['submit'] = 1
    payload['openpage'] = 1
    payload['temporary'] = 1
    payload['data'] = csv
    payload['username'] = 'od2wd'
    payload['token'] = "%242y%2410%24rI5bLyGIWFKgFGeISauRHOeS1S7un5iwlqBDfcWmKHp9LEGqcUKTG"
    payload_str = "&".join("{}={}".format(k,v) for k,v in payload.items())
    final_url="{}?{}".format(url,payload_str)
    print("[Phase-6-{}] Getting publication link :\n {} \n".format(procId,final_url))
    return final_url

def fetch_csv_from_link(url):
    startIdx=url.index("data.")
    fileName = url[startIdx:]

    #check origin
    origin = ""
    location = fileName[5:fileName.index(".go.id")]
    if location in ['jakarta', 'bandung']:
        origin = location
    else:
        origin = ''
    
    queryName = fileName[len(fileName)-fileName[::-1].find('/'):]
    base_url = "http://data.{}.go.id/api/3/action/package_search".format(origin)
    params = {}
    params['q']=queryName
    response = requests.get(url=base_url, params=params)
    json_data = json.loads(response.text)
    fetch_link = json_data['result']['results'][0]['resources'][0]['url']
    file_name=check_file_name('{}.csv'.format(queryName))
    wget.download(fetch_link, 'data/uncleaned/{}'.format(file_name))
    return file_name