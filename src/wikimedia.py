import requests
import json
from SPARQLWrapper import SPARQLWrapper, JSON

def searchEntity(keyword, limit):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent="od2wd/1.0 (https://od2wd.id/about; adm.od2wd@gmail.com) SPARQLWrapper/1.8.2")
    res = requests.get(url)
    return json.loads(res.text)

def searchObjWProperty(subject_id, property_id):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent="od2wd/1.0 (https://od2wd.id/about; adm.od2wd@gmail.com) SPARQLWrapper/1.8.2")

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
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent="od2wd/1.0 (https://od2wd.id/about; adm.od2wd@gmail.com) SPARQLWrapper/1.8.2")

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
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent="od2wd/1.0 (https://od2wd.id/about; adm.od2wd@gmail.com) SPARQLWrapper/1.8.2")

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
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent="od2wd/1.0 (https://od2wd.id/about; adm.od2wd@gmail.com) SPARQLWrapper/1.8.2")

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

