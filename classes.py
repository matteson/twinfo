from twython import Twython
from twython import TwythonStreamer
from string import find
import web
import json
from math import log
from time import time
import nltk
from nltk.collocations import *
bigram_measures = nltk.collocations.BigramAssocMeasures() #for convenience

# silence db logging
web.config.debug = False

class TwitterLogFromStream(TwythonStreamer):
    def __init__(self,newdb,dbname,*params):
        super(TwitterLogFromStream,self).__init__(*params)
        self.db = web.database(dbn='sqlite',db='./' + dbname)
        if newdb:
            self.db.query('''CREATE TABLE tweets (
                text TEXT,
                time INT,
                geek BOOL,
                nerd BOOL
                );''')
            
    def on_success(self, data):
        if 'lang' in data and not data.has_key('retweeted_status'):
            if 'text' in data:
                if data["entities"]["user_mentions"]:
                    text = self.strip_user(data)
                else:
                    text = data['text'].encode('utf-8')

                #print json.dumps(data, sort_keys=True,indent=4, separators=(',', ': '))
                geek = find(text.lower(),u'geek')>-1
                nerd = find(text.lower(),u'nerd')>-1
                print text
                self.db.insert('tweets',
                          text=text,
                          time=int(time()),
                          geek=geek,
                          nerd=nerd
                          );
                          

    def on_error(self, status_code, data):
        if not status_code == 200:
            print status_code

    def strip_user(self,data):
        text=data['text'].encode('utf-8')
        inds = [0]
        for users in data["entities"]["user_mentions"]:
            inds.extend(users["indices"])
        inds.append(len(text))
        stripped_text = ''.join([text[inds[i]:inds[i+1]] for i in range(0,len(inds),2)])
        return stripped_text

class PMICalc:
    def __init__(self,dbNameSample,dbNameCorp,minHits=5):
        # highlight some things that will be assigned properties later
        self.corpFD = nltk.FreqDist()
        self.nerdFD = nltk.FreqDist()
        self.geekFD = nltk.FreqDist()

        self.nerdProb = dict()
        self.geekProb = dict()
        self.corpProb  = dict()

        self.nerdPMI = None
        self.geekPMI = None

        self.nerdFinder = None
        self.geekFinder = None
        
        self.dbSampleText   = web.database(dbn='sqlite',db='./' + dbNameSample)
        self.dbNerdIterator = self.dbSampleText.select('tweets',where="nerd")
        self.dbGeekIterator = self.dbSampleText.select('tweets',where="geek")

        self.dbCorp = web.database(dbn='sqlite',db='./' + dbNameCorp)
        self.dbCorpIterator = self.dbCorp.select('tweets')
        
        self.blockedWords    = [u'geek',u'geeks',u'geeky',
                                u'nerd',u'nerds',u'nerdy']
        self.minHits = minHits

    def compileFreqBase(self,wordIter,freq):
        for tweet in wordIter:
            tokens = nltk.wordpunct_tokenize(tweet.text)
            freq.update([word.lower() for word in tokens])


    def compileFreq(self):
        self.compileFreqBase(self.dbNerdIterator,self.nerdFD)
        self.compileFreqBase(self.dbGeekIterator,self.geekFD)
        self.compileFreqBase(self.dbCorpIterator,self.corpFD)

    def genProbsBase(self,freq,prob):
        N    = freq.N()
        for (word,num) in freq.items():
            if num>self.minHits:
                prob[word] = float(num)/N


    def genProbs(self):
        self.genProbsBase(self.nerdFD,self.nerdProb)
        self.genProbsBase(self.geekFD,self.geekProb)
        self.genProbsBase(self.corpFD,self.corpProb)

    def genPMIBase(self,specificProb,generalProb):
        pmi = [(key,log(specificProb[key]) - log(generalProb[key]))
                                        for key in specificProb.keys()
               if generalProb.has_key(key) and not key in self.blockedWords]
        pmi.sort(key=lambda tup:tup[1],reverse=True)

        return pmi

    def genPMI(self):
        self.nerdPMI = self.genPMIBase(self.nerdProb,self.corpProb)
        self.geekPMI = self.genPMIBase(self.geekProb,self.corpProb)

class Authorize():

    def __init__(self,dbname,newDB=False):
        self.authDB = web.database(dbn='sqlite',db='./' + dbname)
        if newDB:
            self.authDB.query('''CREATE TABLE auth (
                 ID text,
                 APP_KEY text,
                 APP_SECRET text,
                 OAUTH_TOKEN text,
                 OAUTH_TOKEN_SECRET text
                );''')

    def setData(self,ID,APP_KEY,APP_SECRET,OAUTH_TOKEN,OAUTH_TOKEN_SECRET):
        self.authDB.insert('auth',
                           ID=ID,
                           APP_KEY=APP_KEY,
                           APP_SECRET=APP_SECRET,
                           OAUTH_TOKEN=OAUTH_TOKEN,
                           OAUTH_TOKEN_SECRET=OAUTH_TOKEN_SECRET)

    def getData(self,ID):
        selectDict = dict(ID=ID)
        authIter = self.authDB.select('auth',selectDict,where="ID==$ID")
        return authIter.list()[0]

        

