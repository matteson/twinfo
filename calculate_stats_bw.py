from classes import PMICalc
from classes import FreqCompilation
from math import log

def unique(a):
    """ return the list with duplicate elements removed """
    return list(set(a))


wineResultStore = []
beerResultStore = []


freqwine = FreqCompilation('beerwine.db',where='wine')
freqbeer = FreqCompilation('beerwine.db',where='beer')
freqCorp = FreqCompilation('corpusTweets.db')

freqwine.compileFreq()
freqbeer.compileFreq()
freqCorp.compileFreq()

blockedWords = [u'wine',u'wines',u'winey',
                u'beer',u'beers',u'beery']


pmiwine = PMICalc(freqwine.getFreq(),freqCorp.getFreq(),blockedWords,minHits=15)
pmibeer = PMICalc(freqbeer.getFreq(),freqCorp.getFreq(),blockedWords,minHits=15)

pmiwine.calcPMI()
pmibeer.calcPMI()

wineResult = pmiwine.getPMI()
beerResult = pmibeer.getPMI()

wineResultStore.append(wineResult)
beerResultStore.append(beerResult)


print '\n\n', 'winey:', '\n'
for tup in wineResult[0:20]:
    print tup[0], '\t\t', tup[1]

print '\n\n', 'beery:', '\n'
for tup in beerResult[0:20]:
    print tup[0], '\t\t', tup[1]

print '==============================================='


def convertToDict(tupList):
    outDict = {}
    for tup in tupList:
        outDict[tup[0]] = tup[1]
    return outDict

outWine = [tup[0] for tup in wineResult if tup[1]>0]
outBeer = [tup[0] for tup in beerResult if tup[1]>0]
outIntersect = [word for word in outBeer if word in outWine]

outUnion = outWine
outUnion.extend(outBeer)
outUnion = unique(outUnion)

wineDict = convertToDict(pmiwine.getPMI())
beerDict = convertToDict(pmibeer.getPMI())

#out = [(word,wineDict[word],beerDict[word]) for word in outIntersect]

out = []
# need large negative value to be added, on the order of log(15/num_tweets)
for word in outUnion:
    if wineDict.has_key(word):
        wineValue = wineDict[word]
    else:
        wineValue = - log(pmiwine.corpProb[word])
    if beerDict.has_key(word):
        beerValue = beerDict[word]
    else:
        beerValue = - log(pmibeer.corpProb[word])

    out.append((word,wineValue,beerValue))
        

##for tup in out:
##    print tup


##>>> load pickle
##SyntaxError: invalid syntax
##>>> import pickle
##>>> pickle.dump(out,open('Users/Andrew/twitter_app/outUnion.p',"wb"))
##
##Traceback (most recent call last):
##  File "<pyshell#9>", line 1, in <module>
##    pickle.dump(out,open('Users/Andrew/twitter_app/outUnion.p',"wb"))
##IOError: [Errno 2] No such file or directory: 'Users/Andrew/twitter_app/outUnion.p'
##>>> pickle.dump(out,open('/Users/Andrew/twitter_app/outUnion.p',"wb"))
##>>> 

