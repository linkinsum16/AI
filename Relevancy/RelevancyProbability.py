import math
import json

from Relevancy.preprocess import totalnumberoffreq, keywordpositionSum, submition, avg, totalnumberofsentence

def prominanceProbablity(meta,corefs):
    jObj = json.loads(meta)
    # text = jObj['body']
    keywords = str(jObj['keywords'])
    keywordsArray = keywords.split(',')
    arr,mentions = totalnumberoffreq(keywordsArray,corefs)
    keywordCount = str(submition(arr))
    try:
        prominaceRatio = float(avg(keywordpositionSum(corefs,keywordsArray)))/float(totalnumberofsentence(meta))
    except:
        prominaceRatio = 0.0


    coef_keywordCount = 0.0607
    coef_prominaceRatio = -7.0208
    z_Score = float(keywordCount)*coef_keywordCount + float(prominaceRatio) * coef_prominaceRatio
    prob = (1 / (1 + math.exp(-z_Score)) * 100)
    return json.dumps({'relevancy_score' : str(format(prob,'.2f')) })


def trainProminanceProbablity(meta,corefs):
    jObj = json.loads(meta)
    # text = jObj['body']
    keywords = str(jObj['keywords'])
    kwArray = keywords.split(',')
    arr,mentions = totalnumberoffreq(kwArray,corefs)
    keywordCount = str(submition(arr))
    try:
        prominaceRatio = float(avg(keywordpositionSum(corefs[0],kwArray)))/float(totalnumberofsentence(meta))
    except:
        prominaceRatio = 0.0


    coef_keywordCount = 0.0607
    coef_prominaceRatio = -7.0208
    z_Score = float(keywordCount)*coef_keywordCount + float(prominaceRatio) * coef_prominaceRatio
    prob = (1 / (1 + math.exp(-z_Score)) * 100)
    return json.dumps(
        {'relevancy_score' : str(prob) ,
          'z_score' : z_Score,
         'def_coef_keyword_count' : coef_keywordCount,
         'def_coef_prominance_ratio' : coef_prominaceRatio,
         'prominance_ratio' : prominaceRatio,
         'keyword_count' : keywordCount,
         'nlp' : mentions
         })