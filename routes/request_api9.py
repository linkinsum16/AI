from ratelimit import limits

import requests
from flask import jsonify, abort, request, Blueprint
from pandas._libs import json

from Autotagging.TaggingMain import corefrenceResolverAuto
from Autotagging.TaggingProbablity import TaggingProbablity
from Relevancy.RelevancyProbability import prominanceProbablity
from Relevancy.preprocess import corefrenceResolverRelavancy
from Sentiment.sentiment import sentiments
from TextSummary.summarization import corefrenceResolverSummary, Summarymain

REQUEST_API = Blueprint('request_api', __name__)

SummOneMonth=43200



def get_blueprint():
    """Return the blueprint for the main app module"""
    return REQUEST_API

def cleanText(txt):
    import re
    finalText = [re.sub(r"[^a-zA-Z0-9]+", ' ', k) for k in txt.split("\n")]
    return ' '.join(finalText)

@REQUEST_API.route('/summarization', methods=['POST'])
@limits(calls=1, period=SummOneMonth)
def forSummary():

    api_key = request.headers.get('api_key')

    if not request.get_json():
        abort(400)
    if api_key!='123456789' or api_key==None:
        return '401'




    jObj = json.loads((request.data).decode("utf-8"))
    text =  str(jObj['body'])
    corefs = corefrenceResolverSummary(text)
    restp = Summarymain((request.data).decode("utf-8"), corefs)
    return restp, 201



@REQUEST_API.route('/advanced-tag', methods=['POST'])
@limits(calls=1000, period=SummOneMonth)
def advanceTagging():
    api_key = request.headers.get('api_key')

    if not request.get_json():
        abort(400)
    if api_key!='123456789' or api_key==None:
        return '401'

    corefs = corefrenceResolverAuto((request.data).decode("utf-8"))
    corefs = corefs.strip().replace(". ", ".")
    restp = TaggingProbablity(corefs)
    print(restp)
    if restp > .80:
        return json.dumps('SPORTS')
    else:
        return json.dumps('NON-SPORTS')

@REQUEST_API.route('/relevancy', methods=['POST'])
@limits(calls=1000, period=SummOneMonth)
def relevancy():
    api_key = request.headers.get('api_key')
    if api_key!='123456789' or api_key==None:
        return '401'

    jObj = json.loads((request.data).decode("utf-8"))
    text = jObj['body']
    corefs = corefrenceResolverRelavancy(text)

    result = prominanceProbablity((request.data).decode("utf-8"), corefs)
    return result

@REQUEST_API.route('/sentiment', methods=['POST'])
@limits(calls=1000, period=SummOneMonth)
def sentiment():
    api_key = request.headers.get('api_key')



    # if not request.get_json():
    #     abort(400)
    if api_key!='123456789' or api_key==None:
        return '401'
    jObj = json.dumps((request.data).decode("utf-8"))
    jObj=str(jObj).replace('{ "body":','').replace('}','')
    text = cleanText(jObj)
    restp=sentiments(text)
    try:
        return restp
    except:
        return "Not proper sentence"

def getJson(restp:list):
    dict={}
    for i in restp:
        dict[i[0]]=i[1]
    return dict



