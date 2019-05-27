import json
import requests

def test_api(columns, dttype, parentApiUrl="http://od2wd.id/api/"):
    properties = []
    parent_api_link=parentApiUrl
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
    print("PHASE-2, Calling Url for Property Mapping")
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


column=['alamat', 'kelurahan', 'alamat sekolah']
dt_col={'alamat':'String', 'kelurahan':'WikibaseItem', 'alamat sekolah':'WikibaseItem'}
a, b = test_api(column, dt_col, parentApiUrl="http://localhost:8080/")
print(a)
print(b)

