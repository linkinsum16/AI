import math

from Autotagging.ElasticSearchOntology import elasticSearchOntology
from Autotagging.TaggingMain import R1, R2, R3, extractNounsAndVerbs



def TaggingProbablity(corefs):
    sportsWordList = []
    sportsWordCountDict = {}
    uniqueWordList = []

    nounList = extractNounsAndVerbs(corefs)
    for word in nounList:
        if word in sportsWordCountDict.keys():
            sportsWordCountDict[word] += 1
        elif word not in uniqueWordList:
            uniqueWordList.append(word)
            isFoundInES = elasticSearchOntology(word)
            if (isFoundInES):
                sportsWordList.append(word)
                sportsWordCountDict[word] = 1


    sumr1Body= R1.sumR1(corefs,nounList,sportsWordList)
    sumbigramsubjectR2_body = R2.bigramsubjectR2(corefs,nounList,sportsWordList)
    avgR3_body = R3.averageR3(corefs,sportsWordList)

    const = -0.8786
    coef_sumr1Body = 4.4894
    coef_sumbigramsubjectR2_body = 1.4155
    coef_avgR3_body = -1.1073

    z_Score = const + float(sumr1Body) * coef_sumr1Body + float(
        sumbigramsubjectR2_body) * coef_sumbigramsubjectR2_body + float(avgR3_body) * coef_avgR3_body

    prob = 1 / (1 + math.exp(-z_Score))


    return prob
