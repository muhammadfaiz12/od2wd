import os
import platform
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
