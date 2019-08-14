import re
import json
import string
from stanfordcorenlp import StanfordCoreNLP as SFN
import yaml
import os

from Autotagging.TaggingMain import nlp

props = {
        'annotators': 'coref',
        'pipelineLanguage': 'en', 'timeout': '9999999',
    }

dir_path = os.getcwd()
with open(dir_path + "/config.yml", 'r') as yml_file:
    cfg = yaml.load(yml_file)

def connection():
    host = cfg['host']
    port = cfg['port']
    nlp = SFN(host, port, timeout=30000, quiet=True)

    return nlp


def cleandata(text):
    textwospecial = re.sub('[^.,a-zA-Z0-9 \n\']', '', text)
    cleannumber = re.sub('^[0-9]+', '', textwospecial)
    re_float = re.compile('([0-9]\.[0-9]+)')
    cleanfloat = re.sub(re_float, '', cleannumber)

    return cleanfloat


def corefrenceResolverRelavancy(text):
    result = json.loads(nlp.annotate(text, properties=props))
    mentions = result['corefs']
    noun = ''
    text2 = ''
    for mention in mentions:
        # print(mentions[mention][0])
        for ele in mentions[str(mention).lower().strip()]:

            if ele['isRepresentativeMention'] == True:
                noun = ele['text']

            else:
                try:
                    if ele['type'] == 'PRONOMINAL':
                        text2 = re.sub(r"\b%s\b" % ele['text'], noun, text)
                except:
                    print("ERROR")

    if text2 =='' or text2 ==' ':
        puntution = set(r"""!"#$%&'()●|*+,-/:;<=>?@[\]^_`{|}~""")
        clean = ''.join(x for x in text if x not in puntution)
        clean = clean.strip('\"').strip(' ')
        text2 = clean
    return text2, mentions


#
def totalnumberofsentence(text):
    text = cleandata(text)
    text = re.sub('[%s]' % re.escape(string.punctuation.replace('.', '')), '', text)
    text = re.sub(r"\.+", ".", text)
    text = text.replace(' . ', '')

    return text.count('.')

#
def totalnumberoffreq( keywordsArray,corefs):
    cleansentence, mentions = corefs
    ls = {}

    for key in keywordsArray:
        keys = key.rstrip().lower()

        cpunt = cleansentence.rstrip().lower().count(keys)
        if cpunt > 0:
            if keys != '':
                ls[keys] = cpunt
    return ls, mentions


def sumOfFrequency(dict):
    total = sum(dict.values())
    return total


def removestopwords(text):
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    return filtered_sentence


def positionrevelancetokeyword(text, kwArray):
    sentence, mention = text
    index = 0
    position = {}
    keyword = totalnumberoffreq(kwArray,text)
    kls = sentence.split(".")
    for keys in keyword[0].keys():
        pos = []
        for sent in kls:
            if sent.rstrip().lower().count(keys.lower()) > 0:
                pos.append(kls.index(sent) + 1)
        position[keys] = pos
    return position


def keywordpositional(text, kwArray):
    """positon of keyword file in sentence body / total number of sentence"""
    totalnosentence = totalnumberofsentence(text[0])
    # #print(totalnosentence)
    position = positionrevelancetokeyword(text, kwArray)
    # #print(kwposition)
    kwpostion = {}
    keywordpositional = []
    for key, value in position.items():
        keywordpositional = []
        for v in value:
            try:
                keywordpositional.append(v / totalnosentence)
            except:
                print("ZeroDivisionError: division by zero")
            kwpostion[key] = keywordpositional

    return kwpostion


#
def keywordpositionSum(text, kwArray):
    keywords = keywordpositional(text, kwArray)
    keywordsum = {}
    for key, value in keywords.items():
        keywordsum[key] = sum(value)
    return keywordsum


def keywordpositionAvg(text, kwArray):
    keywords = keywordpositional(text, kwArray)
    keywordAvg = {}
    for key, value in keywords.items():
        keywordAvg[key] = sum(value) / len(value)
    return keywordAvg


#
def avg(dict):
    try:
        average = sum(dict.values()) / len(dict.values())
    except:
        average = 0.0
    return average


#
def submition(dict):
    # for key, value in dict.items():
    total = sum(dict.values())
    return total
