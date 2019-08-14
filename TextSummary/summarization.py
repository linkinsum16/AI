import json
from stanfordcorenlp import StanfordCoreNLP
from itertools import chain
import re
import yaml
import os
import string
# host = 'http://159.89.161.55'

dir_path = os.getcwd()
with open(dir_path + "/config.yml", 'r') as yml_file:
   cfg = yaml.load(yml_file)
host = cfg['host']
port = cfg['port']
nlp = StanfordCoreNLP(host, port=port, timeout=30000000, quiet=True)
props = {"annotators": "coref", "date": "2019-01-02T16:21:54"}


def corefrenceResolverSummary(text):
    result = json.loads(nlp.annotate(text, properties=props))
    mentions = result['corefs']
    noun = ''
    text_Coref = ''
    for mention in mentions:
        for i in mentions[str(mention).lower().strip()]:

            if i['isRepresentativeMention'] == True:
                noun = i['text']

            else:
                try:
                    if i['type'] == 'PRONOMINAL':
                        text_Coref = re.sub(r"\b%s\b" % i['text'], noun, text)
                        text_Coref = text_Coref
                except:
                    print("ERROR in Text")
    if text_Coref is '':
        return text
    return text_Coref


def extractNounsAndVerbs(corefs):
    text = corefs
    typesOfNounsAndVerbs = ['NN', 'NNS', 'NNP', 'NNPS', 'VBD', 'VBG']
    nounsAndVerbs = []
    finalListnounAndVerbs = []
    tagged = nlp.pos_tag(text)
    for tag in tagged:
        if typesOfNounsAndVerbs.__contains__(tag[1]):
            nounsAndVerbs += [tag[0]]
            stopWords = ['is', 'was', 'were', 'said',  'had', 'put', 'Were']
            finalListnounAndVerbs = [ele.lower() for ele in nounsAndVerbs if ele not in stopWords]
    return finalListnounAndVerbs

def readOntology():
    with open('keywords.txt', 'r') as csvfile:
        readCSV = csvfile.read().lower().replace('\n', '').split(',')

    return readCSV

def realKeywords(corefs):
    keyword_list = []
    _keyword_fileName = readOntology()
    _keyword_fileName = [x.replace(' ','').strip() for x in _keyword_fileName]
    for ele in extractNounsAndVerbs(corefs):
        if _keyword_fileName.__contains__(str(ele).lower().strip()):
            keyword_list.append(ele)

    return keyword_list



def subject(text,subList):

    # sent = text.strip().split('.')
    # all_subject_list = []


    counter = 1
    sentence = text.replace('\n', '').strip()
    subject_list = []
    tkn = nlp.word_tokenize(sentence)
    dep = nlp.dependency_parse(sentence)

    counter += 1
    for token in dep:
        if str(token[0]) == 'nsubj' or str(token[0]) == 'csubjpass' or str(token[0]) == 'nsubjpass':
            token_position = token[2]
            subject = tkn[token_position - 1]
            subject_list.append(str(subject).lower())

    subList.append(subject_list)


def final_Sub(corefs):
    ls =[]
    subList =list(chain.from_iterable(ls))
    subject(corefs,subList)
    keyword_list = realKeywords(corefs)
    finalList = []
    for subj in subList:
        flag = 0
        for sub in subj:
            if sub in keyword_list:
                flag= 1
        if flag == 1:
            finalList.append(subj)
        else:
            finalList.append([])

    return finalList

class Bigram:

    def findKeywordInOntology(ls: list) -> int:
        ontologyList = readOntology()
        lis = [str(x.lower()).strip() for x in ls]
        bigramCount = 0
        for ele in ls:
            if ontologyList.__contains__(ele.lower().strip()):
                # print(ele)
                if lis.index(ele) != len(lis) - 1:
                    if ontologyList.__contains__(lis[lis.index(ele) + 1]):
                        bigramCount += 1
        return bigramCount

    def bigramPos(corefs:str):

        coreftext =corefs
        cleanedText = coreftext
        sentenceses = cleanedText.split(".")
        countAndPositionOfBigramsDict = {}
        listOfPositions = []
        countOfBigrams = 0
        for sentence in sentenceses:
            listOfNounsAndVerbs = extractNounsAndVerbs(sentence)
            biagrams = Bigram.findKeywordInOntology(listOfNounsAndVerbs)
            if biagrams > 0:
                countOfBigrams += biagrams
                listOfPositions.append(sentenceses.index(sentence))
        countAndPositionOfBigramsDict['noOfBigrams'] = countOfBigrams
        countAndPositionOfBigramsDict['positionOfBigrams'] = listOfPositions

        return countAndPositionOfBigramsDict

def createKeywordFile(keywords):
    f = open("keywords.txt", "w+")
    f.write(keywords)
    f.close()

def Summarymain(reqText,corefs):
    # print(reqText)
    jObj = json.loads(reqText)
    # text = jObj['body']
    keywords = jObj['keywords']
    createKeywordFile(keywords)
    # print("texttasdasdja")
    splittedText = corefs.replace('. ','.').strip().strip().split('.')
    ls =[]
    ls_summary =[]
    if len(final_Sub(splittedText[0])[0]) != 0:
        ls_summary.append(splittedText[0])
    for stext in splittedText[1:]:
        stext = stext.replace('\n', '').strip()
        subList = final_Sub(stext)
        bList = Bigram.bigramPos(stext)

        if len(subList[0]) != 0 and len(bList)!=0:
            ls_summary.append(stext)
    summary = ('.'.join(ls_summary))
    summary_points = summary.split('.')
    # i = 1
    for sent in summary_points:
        ls.append(str(sent))
    returnObject = json.dumps({'data':'\n'.join(ls)})
    return  returnObject

