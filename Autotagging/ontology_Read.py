
import sys
from elasticsearch import Elasticsearch


from operator import itemgetter
from collections import Counter

from Autotagging.TaggingMain import cfg


def most_common(instances):
    """Returns a list of (instance, count) sorted in total order and then from most to least common"""
    return sorted(sorted(Counter(instances).items(), key=itemgetter(0)), key=itemgetter(1), reverse=True)



def executeontology_main(word):
    mid_query = ''
    import re
    for m in re.finditer('\S+', word):
        mid_query+=m.group(0)
    main_query='{"query":{"bool":{"must":[{"term":{"article.ontology.keyword":"'+mid_query+'"}},{"term":{"article.category.keyword":"SPORTS"}},{"match_all":{}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}'
    index_name = cfg['executeontology_main']['index_name']


    es = Elasticsearch([{'host': cfg['executeontology_main']['host'], 'port': cfg['executeontology_main']['port']}])
    d = """"""

    for counter in list(range(1)):
        try:
            searchQuery = str.replace(main_query, "#counter", str(counter))
            rest = es.search(index=index_name, body=searchQuery)
            data = [doc for doc in rest['hits']['hits']]
            for doc1 in data:
                text_to_process = doc1['_source']['article']['category']
                d += ' ' + (text_to_process)

        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e:
            print("Unexpected error:", sys.exc_info()[0])



    import re

    words = re.findall(r"\w+", d)
    frequencies = most_common(words)
    percentages = [(instance, count / len(words)) for instance, count in frequencies]
    dict = {}
    for word, percentage in percentages[:7]:
        dict[word] =  percentage * 100

    return dict