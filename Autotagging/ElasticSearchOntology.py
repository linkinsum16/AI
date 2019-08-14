import operator

from elasticsearch import Elasticsearch

# by default we connect to localhost:9200
from Autotagging.ontology_Read import executeontology_main

# es = Elasticsearch([{'host': '192.168.12.39', 'port': 9200}])


def elasticSearchOntology(word:str):

    try:
        dict = executeontology_main(word.lower())
        if (str(max(dict.items(), key=operator.itemgetter(1))[0]) == 'SPORTS'):
            (word , "SPORTS", dict.get("SPORTS"))
            print(word , "SPORTS", dict.get("SPORTS"))
            return True
        else:
            # print(word,"Non-sports")
            return False


    except:
        # print(word,"Word not found")
        return False




