import os, shelve
import pandas as pd
from src.utils import *
from src.main_utils import get_label_from_map_file

def migrate():
	results_files = os.listdir('data/results')
	results_files.remove('dummy')
	if '-debug' in results_files:
		results_files.remove('-debug')
	db_payload = {}
	s = shelve.open('db/col-db')
	#isi protagonist dan nama colum
	for file_name in results_files:
		print(file_name)
		db_payload = getMapInfo(file_name, db_payload)
		db_payload = getLinkInfo(file_name, db_payload)
		s[file_name]=db_payload
	s.close()

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
			db_payload['column'][key]['linked']=value_arr[1]
			db_payload['column'][key]['results']=value_arr[1]
	return db_payload


	

migrate()