import json
import re
import string

from stanfordcorenlp import StanfordCoreNLP
import time
import os
import yaml
dir_path = os.getcwd()
with open(dir_path + "/config.yml", 'r') as yml_file:
   cfg = yaml.load(yml_file)
host = cfg['host']
port = cfg['port']

nlp = StanfordCoreNLP(host, port=port,
                      timeout=300000000000)
props = {
        'annotators': 'coref',
        'pipelineLanguage': 'en' }
def cleanText(text: str):
    text = re.sub('[%s]' % re.escape(string.punctuation.replace('.', '')), ' ', text)
    text = re.sub(r"\.+", ".", text)
    text = text.replace('"' ,'' )
    text = text.replace('●','')
    text = text.replace('/','')
    text = text.replace('.','. ')


    return text

def corefrenceResolverAuto(text):
    text = text.replace("...", "")
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
                        text_Coref = cleanText(text_Coref)
                except:
                    print("ERROR in Text")
    if text_Coref is '':
        return text
    return text_Coref



def extractNounsAndVerbs(corefs):
    text =corefs
    typesOfNounsAndVerbs = ['NN', 'NNS', 'NNP', 'NNPS', 'VBD', 'VBG']
    nounsAndVerbs = []
    finalListnounAndVerbs = []
    tagged = nlp.pos_tag(text)

    for tag in tagged:
        if typesOfNounsAndVerbs.__contains__(tag[1]):
            nounsAndVerbs += [tag[0]]
            stopWords = ['is', 'was', 'were', 'said',
            'got', 'had', 'put', 'Were', 'thats','km','beats','prodigy','father','judges','minute','taking','km']
            finalListnounAndVerbs = [ele for ele in nounsAndVerbs if ele not in stopWords]
            finalListnounAndVerbs = [ele.lower() for ele in finalListnounAndVerbs]

    return finalListnounAndVerbs





class R1:
    def calculateR1(text: str,ls:list,sportsWordList:list):
        NoOfWordsInCleanedArticle = len(extractNounsAndVerbs(cleanText(text))) - 1
        listOfNounsAndVerbs = ls
        noOfKeywords = 0
        opList = []
        uniqueKeywords = []
        for ele in listOfNounsAndVerbs:
            if sportsWordList.__contains__(ele):
                countOfKeyword = listOfNounsAndVerbs.count(ele.lower().strip())
                noOfKeywords += countOfKeyword

                uniqueKeywords.append(ele)
        uniqueKeywords = list(set(uniqueKeywords))

        try:
            # 1st Logic
            opList.append(len(uniqueKeywords) / NoOfWordsInCleanedArticle)
            # 2nd logic
            opList.append(noOfKeywords / NoOfWordsInCleanedArticle)
        except Exception:
            print("Math Exception in R1")
            #opList.append(0)

        return opList

    def sumR1(text: str,ls:list,sportsWordList:list):
        total_r1 = sum(R1.calculateR1(text,ls,sportsWordList))

        return total_r1

class R2():

    def bigramCount(ls: list,sportsWordList) -> int:
        lis = [str(x.lower()).strip() for x in ls]
        bigramCount = 0
        for ele in ls:

            if sportsWordList.__contains__(ele.strip()):

                if lis.index(ele) != len(lis) - 1:
                    if sportsWordList.__contains__(lis[lis.index(ele) + 1]):
                        bigramCount += 1
        return bigramCount

    def bigram(text:str,sportsWordList):
        textcoref = text
        sentenceses = textcoref.split(".")
        count_and_position_of_bigrams_dict = {}
        list_of_positions = []
        countOfBigrams = 0
        for sentence in sentenceses:
            listOfNounsAndVerbs = extractNounsAndVerbs(sentence)
            biagrams = R2.bigramCount(listOfNounsAndVerbs,sportsWordList)
            if biagrams > 0:
                countOfBigrams += biagrams
                list_of_positions.append(sentenceses.index(sentence))
        count_and_position_of_bigrams_dict['noOfBigrams'] = countOfBigrams
        count_and_position_of_bigrams_dict['positionOfBigrams'] = list_of_positions

        return count_and_position_of_bigrams_dict

    def calculateR2Bigram(countAndPositionOfBigramsDict: dict, text:str):
        pob = countAndPositionOfBigramsDict['positionOfBigrams']
        noOfSentenses = len(text.split('.')) - 1
        ratio = []
        for position in pob:
            try:
                ratio.append(position / noOfSentenses)

            except:
                print("Division by 0 R2Bigram")
        return ratio

    def sumR2_Bigram(text:str,sportsWordList):
        sum_r2_ratio = R2.calculateR2Bigram(R2.bigram(text,sportsWordList), text)

        return sum(sum_r2_ratio)

    def subjectR2(text:str,nounList,sportsWordList):
        textcoref = (text)
        sent = textcoref.strip().split('.')
        all_subject_list = []
        counter = 1
        for s in sent:
            (counter, s.replace('\n', '').strip())
            sentence = s.replace('\n', '').strip()
            subject_list = []
            tkn = nlp.word_tokenize(sentence)
            dep = nlp.dependency_parse(sentence)

            counter += 1
            for token in dep:
                if str(token[0]) == 'nsubj' or str(token[0]) == 'csubjpass' or str(token[0]) == 'nsubjpass':
                    token_position = token[2]
                    subject = tkn[token_position - 1]
                    subject_list.append(subject)

            all_subject_list.append(subject_list)

        final_Subject_List = [item for sublist in all_subject_list for item in sublist]

        listOfNounsAndVerbs = nounList
        noOfKeywords = 0
        noOfSubject = 0
        for sub in final_Subject_List:
            if sportsWordList.__contains__(str(sub).lower().strip()):
                final_subjectcount = final_Subject_List.count(sub)
                noOfSubject += final_subjectcount

        subjectRatio = 0.0
        for ele in listOfNounsAndVerbs:

            if sportsWordList.__contains__(str(ele).lower().strip()):
                countOfKeyword = listOfNounsAndVerbs.count(ele)
                noOfKeywords += countOfKeyword

        try:
            subjectRatio = noOfSubject / noOfKeywords

        except:
            print("Exception Division By Zero subjectR2")
            #subjectRatio = 0.0

        return subjectRatio

    def bigramsubjectR2(text:str,nounList,sportsWordList):
        sumbigramR2 = R2.sumR2_Bigram(text,sportsWordList)
        subR2 = R2.subjectR2(text,nounList,sportsWordList)

        r2 = sumbigramR2 + subR2

        return r2


class R3:
    def keywordCount(keyword: str, text: str) -> int:
        count = 0
        try:
            count = sum(1 for match in re.finditer(r"\b%s\b" % keyword.lower().strip(), text.lower()))
        except:
            print(keyword)
        return count

    def positionOfKeyword(keyword: str, text: str) -> list:
        indices = [idx for idx, word in enumerate(text.split('.'), 1) if
                   word.lower().strip().__contains__(keyword.lower().strip())]
        return indices

    def findMentions(text: str,sportsWordList) -> str:
        _kw_ = []
        _kw_list = {}
        nounsAndVerbs = extractNounsAndVerbs(text)
        for word in nounsAndVerbs:
            if sportsWordList.__contains__(word):
                count = R3.keywordCount(word, text)
                if count > 0:
                    pos = R3.positionOfKeyword(word, cleanText(text))
                    # pos = findKWinString(messege)
                    _kw_list[str(word).lower().strip()] = [count, pos]
        return _kw_list

    def calculateR3(text2:str,sportsWordList):
        keywordPosition = R3.findMentions(text2,sportsWordList)
        dic = {}
        for key in keywordPosition:

            sumofkeywordsposition = sum(keywordPosition[key][1])
            no_of_sentenses = len(text2.split('.')) - 1

            try:
                r3 = sumofkeywordsposition / no_of_sentenses
                dic[key] = r3
            except:
                print("Except")
        return dic


    def averageR3(dic,sportsWordList):
        R3_val = R3.calculateR3(dic,sportsWordList)
        R3_val = R3_val.values()
        avgR3 = 0.0
        try:

            avgR3 = sum(R3_val) / len(R3_val)

        except:
            print("Division by 0 averageR3")
            #avgR3 = 0.0

        return avgR3

#
# if __name__ == '__main__':
#     nouns = []
#     ver = []
#     finalList = []
#     # Starts here
#     with open('fsports.csv') as csvfile:
#         next(csvfile)
#         readCSV = csv.reader(csvfile, delimiter=',')
#         for row in readCSV:
#             _header = row[0]
#             _body = row[1]
#             _xml_file_name = row[2]
#             _article_tag = row[3]
#
#             tempList = []
#             tempDict = {'sumr1Body':R1.sumR1(_body),'sumbigramsubjectR2_body': R2.bigramsubjectR2(_body),'avgR3_body': R3.averageR3(_body),'totalNoOfSentences': len(_body.split('.')) - 1,'XML_FILE_NAME': _xml_file_name,'Article_tag': _article_tag}
#             finalList.append(tempDict)
#             df = pd.read_json(str(json.dumps(finalList)))
#             print(df)
#             df.to_csv('Improved_result.csv')