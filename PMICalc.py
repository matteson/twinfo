import web

# silence db logging
web.config.debug = False

from math import log

import nltk
from nltk.collocations import *
bigram_measures = nltk.collocations.BigramAssocMeasures() #for convenience

class PMICalc:
    def __init__(self,dbname):
        # highlight some things that will be assigned properties later
        self.wordFD = nltk.FreqDist()
        self.nerdFD = nltk.FreqDist()
        self.geekFD = nltk.FreqDist()

        self.nerdProb = dict()
        self.geekProb = dict()
        self.totProb  = dict()

        self.nerdFinder = None
        self.geekFinder = None
        
        self.db = web.database(dbn='sqlite',db='./' + dbname)
        self.dbNerdIterator = self.db.select('tweets',where="nerd")
        self.dbGeekIterator = self.db.select('tweets',where="geek")

        self.blockedWords = [u'geek', u'nerd']
        self.minHits = 5

    def compileFreq(self):

        for tweet in self.dbNerdIterator:
            tokens = nltk.wordpunct_tokenize(tweet.text)
            self.wordFD.update([word.lower() for word in tokens])
            self.nerdFD.update([word.lower() for word in tokens])
        for tweet in self.dbGeekIterator:
            tokens = nltk.wordpunct_tokenize(tweet.text)
            self.wordFD.update([word.lower() for word in tokens])
            self.geekFD.update([word.lower() for word in tokens])

    def genProbs(self):
        nerdN = self.nerdFD.N()
        geekN = self.geekFD.N()
        totN = self.wordFD.N()
        for (word,num) in comp.nerdFD.items():
            self.nerdProb[word] = float(num)/nerdN
            if num<self.minHits:
                break
        for (word,num) in comp.geekFD.items():
            self.geekProb[word] = float(num)/geekN
            if num<self.minHits:
                break
        for (word,num) in comp.wordFD.items():
            self.totProb[word]  = float(num)/totN
            if num<self.minHits: # guaranteed to not break too early
                break

    def genPMI(self):
        self.nerdPMI = [(key,log(self.nerdProb[key]) - log(self.totProb[key]))
                                                      for key in self.nerdProb.keys()]
        self.geekPMI = [(key,log(self.geekProb[key]) - log(self.totProb[key]))
                                                      for key in self.geekProb.keys()]
        self.nerdPMI.sort(key=lambda tup:tup[1],reverse=True)
        self.geekPMI.sort(key=lambda tup:tup[1],reverse=True)
        


comp = PMICalc('test.db')
comp.compileFreq()
comp.genProbs()
comp.genPMI()

print '\n\n', 'Geeky:', '\n'


for tup in comp.geekPMI[0:10]:
    print tup[0], '\t\t', tup[1]

print '\n\n', 'Nerdy:', '\n'

for tup in comp.nerdPMI[0:10]:
    print tup[0], '\t\t', tup[1]

