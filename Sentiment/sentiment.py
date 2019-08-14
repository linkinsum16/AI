from stanfordcorenlp import StanfordCoreNLP
import os
import yaml
import re
import json
dir_path = os.getcwd()
with open(dir_path + "/config.yml", 'r') as yml_file:
    cfg = yaml.load(yml_file)
host = cfg['host']
port = cfg['port']
neg_file="/home/sumit/Desktop/NLP/API_NLP/Sentiment/negative-words.txt"
posi_file="/home/sumit/Desktop/NLP/API_NLP/Sentiment/positive-words.txt"
nlp = StanfordCoreNLP(host, port=port,
                      timeout=300000000000)
def extractNounsAndAdj(Text):
    tagged = nlp.pos_tag(Text)
    return tagged

def tenGram(Text):
    pos = []
    senti_pos = {}
    typesOfNouns = ['NN', 'NNS', 'NNP', 'NNPS']
    ls = extractNounsAndAdj(Text)
    for ele in range(0, len(ls)):
        if ele == 0 and typesOfNouns.__contains__(ls[ele][1]):
            for position in range(0, 5):
                if ls[position][1] == 'JJ' or ls[position][1] == 'JJ' or ls[position][1] == 'JJS':
                    pos.append((ls[ele][0],ls[position][0],position))
                    senti_pos[ls[0][0]] = pos
        if ele > 0 and typesOfNouns.__contains__(ls[ele][1]):
            prevLen = ele - 5
            if prevLen <= 0 and typesOfNouns.__contains__(ls[ele][1]):
                for position in range(ele, -1, -1):
                    tempPos = position-1
                    if ls[position - 1][1] == 'JJ' or ls[position - 1][1] == 'JJR' or ls[position - 1][1] == 'JJS':
                        pos.append((ls[ele][0],ls[position - 1][0],ele-tempPos))
                        senti_pos[ls[0][0]] = pos
            if prevLen > 0 and typesOfNouns.__contains__(ls[ele][1]):
                for position in range(ele, prevLen, -1):
                    tempPos = position - 1
                    if ls[position - 1][1] == 'JJ' or ls[position - 1][1] == 'JJR' or ls[position - 1][1] == 'JJS':
                        pos.append((ls[ele][0], ls[position - 1][0], ele - tempPos))
                        senti_pos[ls[0][0]] = pos
            fwrdLen = ele + 5
            if fwrdLen < len(ls) and typesOfNouns.__contains__(ls[ele][1]):
                for position in range(ele, fwrdLen+1):
                    if ls[position][1] == 'JJ' or ls[position][1] == 'JJR' or ls[position][1] == 'JJS':
                        pos.append((ls[ele][0],ls[position][0],position-ele))
                        senti_pos[ls[0][0]] = pos
            if fwrdLen == len(ls) and typesOfNouns.__contains__(ls[ele][1]):
                for position in range(ele, fwrdLen):
                    if ls[position][1] == 'JJ' or ls[position][1] == 'JJR' or ls[position][1] == 'JJS':
                        pos.append((ls[ele][0], ls[position][0], position - ele))
                        senti_pos[ls[0][0]] = pos
    return pos

def getMinimalDistance(dataList:list):
    data = dataList
    list = []
    nns = []
    for ele in data:
        if ele[0] == data[len(data) - 1][0]:
            if not nns.__contains__(ele[0]):
                list.append(ele)
                nns.append(ele[0])
        else:
            for insider in range(data.index(ele) + 1, len(data)):
                if ele[0] == (data[insider][0]):
                    if ele[2] < data[insider][2]:
                        list.append(ele)
                        nns.append(ele[0])
                    else:
                        list.append(data[insider])
                        nns.append(data[insider][0])
                else:
                    if not nns.__contains__(ele[0]):
                        list.append(ele)
                        nns.append(ele[0])
    return set(list)

def read_text(Text):
    Text = re.sub("\s\s+", " ", Text)
    if len(Text.split(' ')) >= 5:
        dataList = tenGram(Text)
        nounAdjPosList = getMinimalDistance(dataList)
        return list(nounAdjPosList)
    else:
        return("Give more words ")

def cleanText(text: str):
    finalText = [re.sub(r"[^a-zA-Z0-9.]+", ' ', k) for k in text.split("\n")]
    return ' '.join(finalText).replace('.',' .')

def dataClean(sentArray,data):
    if(len(data) > 1 ):
        for element in sentArray:
            if element == data :
                return False
        return True
    else:
        return False

def sentiments(Text:str):
    Text = cleanText(Text)
    list_Text = Text.split(' ')

    nounAdjPosList = read_text(Text)
    positive_sentiment=[]
    negative_sentiment=[]
    neutral_sentiment=[]
    positiveset = set()
    negativeset = set()
    neutralset = set()
    for data in nounAdjPosList:
        flag = False
        if isinstance(nounAdjPosList, (list)):
            if list_Text.index(data[1]) == 0 or list_Text.index(data[1])>3:
                for adj in range(list_Text.index(data[1]),list_Text.index(data[1])-5,-1):
                    if str(list_Text[adj]).strip() == 'not':
                        if(dataClean(negative_sentiment,data[0])):
                            negative_sentiment.append(data[0])
                        flag =True

            if flag == False:
                if data[1].lower() in open(posi_file).read().split(", "):
                    if(dataClean(positive_sentiment,data[0])):
                        positive_sentiment.append(data[0])

                elif data[1].lower() in open(neg_file).read().split(", "):
                        negative_sentiment.append(data[0])
                else:
                    if(dataClean(neutral_sentiment,data[0])):
                        neutral_sentiment.append(data[0])

        else:
            return ("Give more words ")
    senti_dict = {"POSITIVE" :sorted(positive_sentiment), "NEGATIVE" :sorted(negative_sentiment), "NEUTRAL" : sorted(neutral_sentiment)}


    all_list = list(senti_dict.values())[0] + list(senti_dict.values())[1] + list(senti_dict.values())[2]

    for word in all_list:
        positive_Count = senti_dict.get("POSITIVE").count(word)
        negative_Count = senti_dict.get("NEGATIVE").count(word)
        neutral_Count = senti_dict.get("NEUTRAL").count(word)
        if (positive_Count > negative_Count) and (positive_Count > neutral_Count):
            positiveset.add(word.lower())
        elif (negative_Count > positive_Count) and (negative_Count > neutral_Count):
            negativeset.add(word.lower())
        else:
            neutralset.add(word.lower())



    return (json.dumps({"POSITIVE": sorted((positiveset)), "NEGATIVE": sorted(set(negativeset)), "NEUTRAL": sorted((neutralset))}))
