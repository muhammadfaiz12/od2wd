import csv
import pandas as pd
from src.wikimedia import searchEntity, searchObjWProperty, searchProperty
from dateutil.parser import parse
import operator
from src.indexer import connect_elasticsearch, search
import logging
import json
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

property_index = 'wd_property'
entity_index = 'wd_entity'
property_doc_type = 'members'

def lDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

def mpNoRankFuzzy(header_list, thresh=0):
    logging.basicConfig(level=logging.ERROR)
    es = connect_elasticsearch()

    result = {}
    resultLabel = {}
    for elem in header_list:
        elem = elem.replace('_', ' ')
        search_object = {
            "query": {
                "match" : {
                    "alias" : {
                        "query": elem,
                        "fuzziness": "AUTO"
                    }
                }
            }
        }
        
        res = search(es, property_index, json.dumps(search_object))['hits']['hits']
        if(len(res) > 0 and res[0]['_score'] > thresh):
            result[elem] = res[0]['_source']['id']
            resultLabel[elem] = res[0]['_source']['label']
        else:
            result[elem] = ''
            resultLabel[elem] = ''
    return result, resultLabel

def mpNoRank(header_list, thresh=0):
    logging.basicConfig(level=logging.ERROR)
    es = connect_elasticsearch()

    result = {}
    resultLabel = {}
    for elem in header_list:
        elem = elem.replace('_', ' ')
        search_object = {
            "query": {
                "match" : {
                    "alias" : {
                        "query": elem,
                        "fuzziness": "AUTO"
                    }
                }
            }
        }
        
        res = search(es, property_index, json.dumps(search_object))['hits']['hits']
        if(len(res) > 0 and res[0]['_score'] > thresh):
            result[elem] = res[0]['_source']['id']
            resultLabel[elem] = res[0]['_source']['label']
        else:
            result[elem] = ''
            resultLabel[elem] = ''
    return result, resultLabel

def mpNoRankWType(header_list, type_list, thresh=0):
    logging.basicConfig(level=logging.ERROR)
    es = connect_elasticsearch()

    result = {}
    resultLabel = {}
    for elem in header_list:
        elem = elem.replace('_', ' ')
        search_object = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {"data type": type_list[header_list.index(elem)]}
                        },
                        {
                            "bool": {
                                "should": [
                                    {"match": {"aliasId": elem}},
                                    {"match": {"aliasEn": elem}}
                                ]
                            }
                        }
                    ]
                }
            }
        }
        
        res = search(es, property_index, json.dumps(search_object))['hits']['hits']
        if(len(res) > 0 and res[0]['_score'] > thresh):
            result[elem] = res[0]['_source']['id']
            resultLabel[elem] = res[0]['_source']['labelId']
        else:
            result[elem] = ''
            resultLabel[elem] = ''
    return result, resultLabel

def mpRankWType(header_list, type_list, thresh=0):
    logging.basicConfig(level=logging.ERROR)
    es = connect_elasticsearch()

    result = {}
    resultLabel = {}
    for elem in header_list:
        elem = elem.replace('_', ' ')
        search_object = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {"data type": type_list[header_list.index(elem)]}
                        },
                        {
                            "bool": {
                                "should": [
                                    {"match": {"aliasId": elem}},
                                    {"match": {"aliasEn": elem}}
                                ]
                            }
                        }
                    ]
                }
            }
        }
        
        res = search(es, property_index, json.dumps(search_object))['hits']['hits']
        if(len(res) > 0):
            found = False
            for cand in res:
                if(elem.lower() in cand['_source']['label']):
                    result[elem] = cand['_source']['id']
                    resultLabel[elem] = cand['_source']['label']
                    found = True
                    break
                if(not found):
                    for cand in res:
                        if(elem.lower() in cand['_source']['alias']):
                            result[elem] = cand['_source']['id']
                            result[elem] = cand['_source']['label']
                            found = True
                            break
                if(not found):
                    split = elem.split()
                    for word in split:
                        for cand in res:
                            for candword in cand['_source']['alias']:
                                if(word.lower() in candword):
                                    result[elem] = cand['_source']['id']
                                    resultLabel[elem] = cand['_source']['label']
                                    found = True
                                    break
                            if(found):
                                break
                        if(found):
                            break
                if(not found):
                    for cand in res:
                        if(elem.lower() in cand['_source']['description']):
                            result[elem] = cand['_source']['id']
                            resultLabel[elem] = cand['_source']['label']
                            found = True
                            break
                if(not found):
                    minDist = 10000
                    candItem = None
                    temp = 0
                    for cand in res:
                        for alt in cand['_source']['alias']:
                            temp = min(minDist, lDistance(elem.lower(), alt))
                        if(temp < minDist):
                            candItem = cand
                            minDist = temp

                    if(candItem['_score'] > 18 and minDist < 8):
                        result[elem] = cand['_source']['id']
                        resultLabel[elem] = cand['_source']['label']
                    else:
                        result[elem] = ''
                        resultLabel[elem] = ''
                    
    return result, resultLabel

def mpRank(header_list, thresh=0):
    logging.basicConfig(level=logging.ERROR)
    es = connect_elasticsearch()

    result = {}
    resultLabel = {}
    for elem in header_list:
        elem = elem.replace('_', ' ')
        search_object = {
            "query": {
                "match" : {
                    "alias" : elem
                }
            }
        }
        
        res = search(es, property_index, json.dumps(search_object))['hits']['hits']
        if(len(res) > 0):
            found = False
            for cand in res:
                if(elem.lower() in cand['_source']['label']):
                    result[elem] = cand['_source']['id']
                    resultLabel[elem] = cand['_source']['label']
                    found = True
                    break
                if(not found):
                    for cand in res:
                        if(elem.lower() in cand['_source']['alias']):
                            result[elem] = cand['_source']['id']
                            result[elem] = cand['_source']['label']
                            found = True
                            break
                if(not found):
                    split = elem.split()
                    for word in split:
                        for cand in res:
                            for candword in cand['_source']['alias']:
                                if(word.lower() in candword):
                                    result[elem] = cand['_source']['id']
                                    resultLabel[elem] = cand['_source']['label']
                                    found = True
                                    break
                            if(found):
                                break
                        if(found):
                            break
                if(not found):
                    for cand in res:
                        if(elem.lower() in cand['_source']['description']):
                            result[elem] = cand['_source']['id']
                            resultLabel[elem] = cand['_source']['label']
                            found = True
                            break
                if(not found):
                    minDist = 10000
                    candItem = None
                    temp = 0
                    for cand in res:
                        for alt in cand['_source']['alias']:
                            temp = min(minDist, lDistance(elem.lower(), alt))
                        if(temp < minDist):
                            candItem = cand
                            minDist = temp

                    if(candItem['_score'] > 18 and minDist < 8):
                        result[elem] = cand['_source']['id']
                        resultLabel[elem] = cand['_source']['label']
                    else:
                        result[elem] = ''
                        resultLabel[elem] = ''
                    
    return result, resultLabel

def mpRankWTypeSim(header_list, type_list, thresh=0):
    print("AAAA")
    namaFileModel = "data/dump/w2vec_wiki_id_case"
    model = Word2Vec.load(namaFileModel)
    print("kicut")
    logging.basicConfig(level=logging.ERROR)
    es = connect_elasticsearch()
    print("connected")

    result = {}
    resultLabel = {}
    for elem in header_list:
        elem = elem.replace('_', ' ')
        search_object = {
            "from" : 0, 
            "size" : 100,
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {"data type": type_list[header_list.index(elem)]}
                        },
                        {
                            "bool": {
                                "should": [
                                    {"match": {"aliasId": elem}},
                                    {"match": {"aliasEn": elem}}
                                ]
                            }
                        }
                    ]
                }
            }
        }
        
        res = search(es, property_index, json.dumps(search_object))['hits']['hits']
        if(len(res) > 0):
            words = elem.split()
            for item in res:
                sim_score = 0
                label = item['_source']['labelId']
                alias = item['_source']['aliasId']
                lwords = label.split()
                for n in range(len(words)):
                    try:
                        sim_score = sim_score + model.similarity(words[n].lower(), lwords[n].lower())
                    except:
                        pass

                for alt in alias:
                    temp = 0
                    alt_words = alt.split()
                    for n in range(len(words)):
                        try:
                            temp = temp + model.similarity(words[n].lower(), alt_words[n].lower())
                        except:
                            pass
                    if(temp > sim_score):
                        sim_score = temp
                item['_score'] = sim_score
                newlist = sorted(res, key=lambda k: k['_score'], reverse=True)
                result[elem] = newlist[0]['_source']['id']
                resultLabel[elem] = newlist[0]['_source']['labelId']
        else:
            result[elem] = ''
            resultLabel[elem] = ''
    return result, resultLabel

def mapProperty(header_list, protagonist):
    logging.basicConfig(level=logging.ERROR)
    es = connect_elasticsearch()

    result = {}
    resultLabel = {}
    for elem in header_list:
        elem = elem.replace('_', ' ')
        search_object = {
            'query': {
                'multi_match': {
                    'query': elem,
                    'fields': 'alias'
                }
            }
        }
        
        res = search(es, property_index, json.dumps(search_object))['hits']['hits']
        if(len(res) > 0):
            found = False
            for cand in res:
                if(elem.lower() in cand['_source']['label']):
                    result[elem] = cand['_source']['id']
                    resultLabel[elem] = cand['_source']['label']
                    found = True
                    break
            if(not found):
                for cand in res:
                    if(elem.lower() in cand['_source']['alias']):
                        result[elem] = cand['_source']['id']
                        result[elem] = cand['_source']['label']
                        found = True
                        break
            if(not found):
                split = elem.split()
                for word in split:
                    for cand in res:
                        for candword in cand['_source']['alias']:
                            if(word.lower() in candword):
                                result[elem] = cand['_source']['id']
                                resultLabel[elem] = cand['_source']['label']
                                found = True
                                break
                        if(found):
                            break
                    if(found):
                        break
            if(not found):
                for cand in res:
                    if(elem.lower() in cand['_source']['description']):
                        result[elem] = cand['_source']['id']
                        resultLabel[elem] = cand['_source']['label']
                        found = True
                        break
            if(not found):
                minDist = 10000
                candItem = None
                temp = 0
                for cand in res:
                    for alt in cand['_source']['alias']:
                        temp = min(minDist, lDistance(elem.lower(), alt))
                    if(temp < minDist):
                        candItem = cand
                        minDist = temp
                
                if(candItem['_score'] > 18 and minDist < 8):
                    result[elem] = cand['_source']['id']
                    resultLabel[elem] = cand['_source']['label']
                    
    return result, resultLabel
