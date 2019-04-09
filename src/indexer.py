from elasticsearch import Elasticsearch
import logging

def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Connected to ES Service')
    else:
        print('Could not connect to ES Service')
    return _es

def create_index(es_object, index_name='wd_property'):
    created = False
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "similarity": {
                "scripted_tfidf": {
                    "type": "scripted",
                    "script": {
                        "source": "double tf = 1.0; double idf = 1.0; double norm = 1/Math.sqrt(doc.length); return query.boost * tf * idf * norm;"
                        }
                }
            },
            "analysis": {
              "analyzer": {
                "trigram_analyzer": {
                  "tokenizer": "trigram"
                },
                "lowercase_analyzer":{
                    "type": "custom",
                    "tokenizer":"standard",
                    "filter":["lowercase"]
                }
              },
              "tokenizer": {
                "trigram": {
                  "type": "ngram",
                  "min_gram": 3,
                  "max_gram": 3,
                  "token_chars": [
                    "letter",
                    "digit"
                  ]
                }
              }
          }
        },
        "mappings": {
            "members": {
                "dynamic": "strict",
                "properties": {
                    "labelId": {
                        "type": "text",
                        "analyzer": "lowercase_analyzer"
                    },
                    "labelEn": {
                        "type": "text",
                        "analyzer": "lowercase_analyzer"
                    },
                    "id": {
                        "type": "keyword"
                    },
                    "aliasId": {
                        "type": "text",
                        "similarity": "scripted_tfidf",
                        "analyzer": "lowercase_analyzer"
                    },
                    "aliasEn": {
                        "type": "text",
                        "similarity": "scripted_tfidf",
                        "analyzer": "lowercase_analyzer"
                    },
                    "descriptionId": {
                        "type": "text",
                        "analyzer": "lowercase_analyzer"
                    },
                    "descriptionEn": {
                        "type": "text",
                        "analyzer": "lowercase_analyzer"
                    },
                    "data type": {
                        "type": "keyword"
                    }
                }
            }
        }
    }
    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_object.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index with name {}'.format(index_name))
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created

def store_record(elastic_object, index_name, record):
    stored = False
    try:
        outcome = elastic_object.index(index=index_name, doc_type='members', body=record)
        stored = True
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))
    finally:
        return stored

def search(es_object, index_name, search):
    res = es_object.search(index=index_name, body=search)
    return res