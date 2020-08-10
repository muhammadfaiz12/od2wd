import os, shelve
import pandas as pd
from src.utils import *
from src.main_utils import get_label_from_map_file
from var_settings import *

def migrate(file_name=""):
	results_files=[]
	if len(file_name) < 1:
		results_files = os.listdir('data/results')
		results_files.remove('dummy')
	else:
		results_files=[file_name]

	if '-debug' in results_files:
		results_files.remove('-debug')
	db_payload = {}
	s = shelve.open('db/col-db')
	errors = []
	#isi protagonist dan nama colum
	for file_name in results_files:
		print(file_name)
		try:
			db_payload = getMapInfo(file_name, db_payload)
			db_payload = getLinkInfo(file_name, db_payload)
		except Exception as e:
			print("error \n {}".format(e))
			errors.append(file_name)
		s[file_name]=db_payload
	print("Success : {}, Fail: {}".format(str(len(results_files)), str(len(errors))))
	s.close()

def migrate_write_metadata(metadata: dict):
	with shelve.open('db/metadata-db') as s:
		s["metadata"] = metadata

def migrate_read_metadata() -> dict:
	with shelve.open('db/metadata-db') as s:
		temp = {}
		if "metadata" in s.keys():
			temp = s["metadata"]
		return temp

def getMapInfo(file_name, db_payload):
    df = load_data(file_name, "mapped")
    #extract protagonist
    columns = df.columns
    protagonist=""
    for col in columns:
    	if "[Protagonist]" in col:
    		protagonist = col[:col.find('-')]
    		db_payload['protagonist-column']=protagonist
    #extract columns name
    column = {}
    for col in columns:
    	col_name = col[:col.find('-')]
    	# db_payload['column'][col_name]['mapped']=col
    	column[col_name]={}
    	column[col_name]['mapped']=col
    db_payload['column']=column
    return db_payload


def getLinkInfo(file_name, db_payload):
	df = load_data(file_name, "linked")
	mapping = get_label_from_map_file(file_name)
	processed_columns = []
	same_col=1
	for key, value in db_payload['column'].items():
		value = value['mapped']
		value_arr = value.split('-')
		if value_arr[1] == 'Padanan Tidak Ditemukan':
			db_payload['column'][key]['linked']=None
			db_payload['column'][key]['results']=None
		elif value_arr[1] == '[Protagonist]':
			db_payload['column'][key]['linked']=key
			db_payload['column'][key]['results']='qid'
		else:
			if processed_columns.count(value_arr[1]) == 0:
				db_payload['column'][key]['linked']=value_arr[1]
				db_payload['column'][key]['results']=value_arr[1]
			else:
				same_name_counter = processed_columns.count(value_arr[1])
				db_payload['column'][key]['linked']="{}({})".format(value_arr[1], str(same_col+1))
				#special case merged on P625-latitude and longitude
				if value_arr[1]=="P625":
					db_payload['column'][key]['results']=value_arr[1]
				else:
					db_payload['column'][key]['results']="{}({})".format(value_arr[1], str(same_name_counter+1))
				same_col+=1
		processed_columns.append(value_arr[1])
	return db_payload

