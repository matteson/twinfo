from classes import PMICalc
from classes import FreqCompilation
from math import log

def unique(a):
    """ return the list with duplicate elements removed """
    return list(set(a))

def convertToDict(tupList):
    outDict = {}
    for tup in tupList:
        outDict[tup[0]] = tup[1]
    return outDict

def calculateStats(db1,db2,dbCorpus,where1,where2,blockedWords=[]):
    word1ResultStore = []
    word2ResultStore = []


    freqword1 = FreqCompilation(db1,where=where1)
    freqword2 = FreqCompilation(db2,where=where2)
    freqCorp = FreqCompilation(dbCorpus)

    freqword1.compileFreq()
    freqword2.compileFreq()
    freqCorp.compileFreq()

    pmiword1 = PMICalc(freqword1.getFreq(),freqCorp.getFreq(),blockedWords,minHits=15)
    pmiword2 = PMICalc(freqword2.getFreq(),freqCorp.getFreq(),blockedWords,minHits=15)

    pmiword1.calcPMI()
    pmiword2.calcPMI()

    word1Result = pmiword1.getPMI()
    word2Result = pmiword2.getPMI()

    word1ResultStore.append(word1Result)
    word2ResultStore.append(word2Result)


    print '\n\n', 'Associated with word1:', '\n'
    for tup in word1Result[0:20]:
        print tup[0], '\t\t', tup[1]

    print '\n\n', 'Associated with word2:', '\n'
    for tup in word2Result[0:20]:
        print tup[0], '\t\t', tup[1]

    print '==============================================='


    outword1 = [tup[0] for tup in word1Result if tup[1]>0]
    outword2 = [tup[0] for tup in word2Result if tup[1]>0]
    outIntersect = [word for word in outword2 if word in outword1]

    outUnion = outword1
    outUnion.extend(outword2)
    outUnion = unique(outUnion)

    word1Dict = convertToDict(pmiword1.getPMI())
    word2Dict = convertToDict(pmiword2.getPMI())

    #out = [(word,word1Dict[word],word2Dict[word]) for word in outIntersect]

    out = []
    # need large negative value to be added, on the order of log(15/num_tweets)
    for word in outUnion:
        if word1Dict.has_key(word):
            word1Value = word1Dict[word]
        else:
            word1Value = log(float(1)/pmiword1.sampleFD.N())- log(pmiword1.corpProb[word])
        if word2Dict.has_key(word):
            word2Value = word2Dict[word]
        else:
            word2Value =  log(float(1)/pmiword2.sampleFD.N())- log(pmiword2.corpProb[word])

        out.append((word,word1Value,word2Value))
            

    return out
