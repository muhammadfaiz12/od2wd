from indexer import connect_elasticsearch, create_index, store_record, search
import logging
import json

property_index = 'wd_property'
entity_index = 'wd_entity'
property_doc_type = 'members'

with open('data/dump/property.json') as f:
    prop_datas = json.load(f)
prop_datas

logging.basicConfig(level=logging.ERROR)
es = connect_elasticsearch()
if(create_index(es, property_index) and create_index(es, entity_index)):
    count = 0
    for elem in prop_datas:
        prop_data = json.dumps(elem)
        
        if(not store_record(es, property_index, prop_data)):
            break
        else:
            count = count + 1
            if(count % 100 == 0):
                print("nums of data stored: {}".format(count))

    print("finish")
    print("total data stored: {}".format(count))