import requests
import json
from SPARQLWrapper import SPARQLWrapper, JSON

def searchEntity(keyword, limit):
    url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search={}&limit={}&language=id&format=json".format(keyword,limit)
    res = requests.get(url)
    return json.loads(res.text)

def searchObjWProperty(subject_id, property_id):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery("""
    SELECT ?item ?itemLabel
    WHERE
    {
        wd:%s wdt:%s ?item .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "id" }
    }
    """ % (subject_id, property_id))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

def searchSbjWProperty(object_id, property_id):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery("""
    SELECT ?item ?itemLabel
    WHERE
    {
        ?item wdt:%s wd:%s .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "id" }
    }
    """ % (property_id, object_id))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

def searchProperty(subject_id, object_id):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery("""
    SELECT ?item ?itemLabel
    WHERE
    {
        wd:%s ?item wd:%s .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "id" }
    }
    """ % (subject_id, object_id))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

def searchPropertyRange(property_id):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery("""
    #Subproperties of location (P276)
    SELECT ?wbtype 
    WHERE {
    wd:%s wikibase:propertyType  ?wbtype.
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    """ % (property_id))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

