import json
import requests

def test_publish_qs(procId):
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
    print(csv)
    print(payload['token'] )
    payload_str = "&".join("{}={}".format(k,v) for k,v in payload.items())
    final_url="{}?{}".format(url,payload_str)
    print(final_url)
  
def test_publish_qs_direct(procId):
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
    payload['submit'] = 1
    payload['username'] = 'od2wd'
    payload['token'] = "%242y%2410%24rI5bLyGIWFKgFGeISauRHOeS1S7un5iwlqBDfcWmKHp9LEGqcUKTG"
    payload['format'] = 'csv'
    payload['data'] = csv
    payload['batchname'] = 'od2wd-wikidata-integration'
    # payload['openpage'] = 1
    # payload['temporary'] = 1
    payload_str = "&".join("{}={}".format(k,v) for k,v in payload.items())
    response = requests.post(url, params=payload_str)
    print(response.url)
    print(response.text)

test_publish_qs("test-qs.csv")
test_publish_qs_direct("test-qs.csv")