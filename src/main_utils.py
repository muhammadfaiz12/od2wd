import os
import pandas

def get_catalogue():
    listOfFile = os.listdir('data/uncleaned/')
    return listOfFile

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
            mapped_columns.append(mapping[col])
        except KeyError:
            mapped_columns.append("padanan tidak ditemukan")
    df.columns = mapped_columns
    df.to_csv("data/mapped/{}".format(procId))
    return

def save_linking_result(df, procId):
    df.to_csv("data/linked/{}".format(procId))
    return

def get_job_status(procId):
    result = []
    states = ['uncleaned', 'processed', 'mapped', 'linked', 'results']
    for state in states:
        status = os.path.isfile('data/{}/{}'.format(state, procId))
        result.append(status)
    return result