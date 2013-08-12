from twython import Twython
from twython import TwythonStreamer
from string import find, Template
import web
from math import log
import time
import nltk
from nltk.collocations import *
bigram_measures = nltk.collocations.BigramAssocMeasures() #for convenience
import sqlite3


# silence db logging
web.config.debug = False

def unique(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

class DataHandler():
    # A super class to handle tweet data and meta data from any api endpoint accessed through Twython
    # NB this data handler is opinionated about what text to include, like stripping usernames, and matching
    # any case of search terms for purposes of logging
    def super_setup(self,newdb,dbname,searchTerms):
        # subclass needs multiple setup functions, call this after the super(Twython).__init__
        self.searchTerms = searchTerms
        self.searchString = self.getSearchString(searchTerms)
        dbString     = self.getDBString(searchTerms)
        self.insertTemplate = self.getInsertTemplate(searchTerms)
        
        self.db = web.database(dbn='sqlite',db='./' + dbname)
        self.conn = sqlite3.connect('./' + dbname)
        self.cursor = self.conn.cursor()

        baseDBString = '''CREATE TABLE tweets (
                text TEXT,
                time INT'''
       
        if newdb:
            self.cursor.execute(baseDBString + dbString + ');')
        self.queryIter = 0

    def getSearchString(self,searchTerms):
        return ' OR '.join(searchTerms)

    def getDBString(self,searchTerms):

        dbString = ' BOOL, '.join(searchTerms)
        if dbString:
            dbString = ', ' + dbString + ' BOOL' #TODO: escape sql char, or figure out how to make DB properly
        return dbString # returns empty string if no search terms

    def getInsertTemplate(self,searchTerms):

        variableTemplate  = ','.join(searchTerms)
        if variableTemplate: # need another comma if nonempty search terms, otherwise, need empty string
            variableTemplate = ',' + variableTemplate 
        
        valueTemplate = "(?,?" + ',?'*len(searchTerms) + ")" # 2 for time/text, others for searchTerms
        tableTemplate = "(text,time" + variableTemplate + ")"

        templateString = 'INSERT INTO tweets ' + tableTemplate + ' VALUES ' + valueTemplate + ';'
        
        return templateString
    
    def handle_data(self, data):
        # generic handler for tweet, stores text content of tweet and true/false flag for each
        # search term in stream or query request
        if 'lang' in data and not data.has_key('retweeted_status'):
            if 'text' in data:
                if data["entities"]["user_mentions"]:
                    dataTup = (self.strip_user(data),)
                else:
                    dataTup = (data['text'],)

                dataTup += (int(time.time()),) # current unix time as int, TODO: could be datetime in future, should be tweet creation time, but currently not
                
                for term in self.searchTerms:
                    dataTup += (1 if dataTup[0].lower().find(term)>-1 else 0,) # python doesn't have true ternary operator, need 1/0 as true/false for sql insert
                
                print dataTup[0] # print tweet text, should be optional?
                
                self.cursor.execute(self.insertTemplate,dataTup)

                self.conn.commit()
                
    def strip_user(self,data):
        # user mentions are often highly correlated with word use, useful to remove them when logging tweets
        # TODO: remove tweets that were selected based on word use due to username
        text=data['text']
        inds = [0]
        for users in data["entities"]["user_mentions"]:
            inds.extend(users["indices"])
        inds.append(len(text))
        stripped_text = ''.join([text[inds[i]:inds[i+1]] for i in range(0,len(inds),2)])
        return stripped_text    

class TwitterLogFromQuery(Twython,DataHandler):
    # query endpoint, search terms required
    # TODO: does this support all query styles?
    def __init__(self,newdb,dbname,searchTerms,*params):
        super(TwitterLogFromQuery,self).__init__(*params)
        self.super_setup(newdb,dbname,searchTerms)

    def beginQuery(self):
        since_id =u'0'
        while True:
            # TODO1: narrow request error and reduce scope of try/except block to only handle it
            # TODO2: figure out cause of requests error
            #try:
                search = self.search(q=self.searchString,lang='en',since_id=since_id,count=100)
                since_id=search[u'search_metadata'][u'max_id_str']

                for data in search[u'statuses']:
                    self.handle_data(data)

                time.sleep(15) # don't hit servers too hard, you will be blocked
                self.queryIter = self.queryIter+1
           # except Exception as inst:
#                print inst
                    

class TwitterLogFromStream(TwythonStreamer,DataHandler):
    # stream endpoint, search terms optional
    def __init__(self,newdb,dbname,searchTerms=[],timeout=float('inf'),*params):
        super(TwitterLogFromStream,self).__init__(*params)
        self.super_setup(newdb,dbname,searchTerms)
        self.timeout = timeout
            
    def on_success(self, data):
        self.handle_data(data)
        if int(time.time()) > self.timeout:
            self.disconnect()
            print 'Disconnected due to user defined timeout'                                         

    def on_error(self, status_code, data):
        if not status_code == 200: # occasionally recieve 200 as an error code, weird?
            print status_code

class Authorize():
    # a lightweight class to create/access an authorization database
    # TODO: is this the secure way to handle secrets?
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


class FreqCompilation:
    # get word use counts from a database and optional where clause
    # TODO: is there ever a situtation where I want to initialize and not immediately get word count
    # should this be a default?
    def __init__(self,dbName,where=None):
        #handle inputs
        self.corpFD = nltk.FreqDist()
        
        #setup databse
        self.dbCorp = web.database(dbn='sqlite',db='./' + dbName)
        if where:
            self.dbIterator = self.dbCorp.select('tweets',where=where)
        else:
            self.dbIterator = self.dbCorp.select('tweets')
        

    def compileFreq(self):
        for tweet in self.dbIterator:
            tokens = nltk.wordpunct_tokenize(tweet.text)
            self.corpFD.update([word.lower() for word in tokens])

    def getFreq(self):
        return self.corpFD

class PMICalc:
    def __init__(self,sampleFreq,corpFreq,blockedWords=[],minHits=5):
        # TODO: consider handling multiple distributions at once here
        self.corpFD   = corpFreq
        self.sampleFD = sampleFreq

        self.sampleProb = dict()
        self.corpProb  = dict()

        self.pmi = None

        self.minHits = minHits
        self.blockedWords = blockedWords
        self.probFlag = False # used in convenience option

    def genProbsBase(self,freq,prob):
        N    = freq.N()
        for (word,num) in freq.items():
            if num>self.minHits:
                prob[word] = float(num)/N

    def calcProbs(self):
        self.genProbsBase(self.sampleFD,self.sampleProb)
        self.genProbsBase(self.corpFD,self.corpProb)
        self.probFlag = True

    def calcPMI(self):
        if not self.probFlag: # calculate probs if not already done
            self.calcProbs()
        N = self.corpFD.N()
    
        self.pmi = [(key,log(self.sampleProb[key]) - log(self.corpProb[key]))
                                        for key in self.sampleProb.keys()
               if self.corpProb.has_key(key) and not key in self.blockedWords]
        self.pmi.sort(key=lambda tup:tup[1],reverse=True)

    def getProb(self,returnCorp=False):
        if returnCorp:
            return self.corpProb
        else:
            return self.sampleProb

    def getPMI(self):
        return self.pmi


class FreqLogger:
    # a simple class to log calculated frequencies or probabilities
    # propbably broken right now
    # TODO: fix or remove
    def __init__(self,newdb,dbName,keys,freq,start,end):

        self.keys  = keys
        self.freq  = freq
        self.start = start
        self.end   = end
        
        self.dbFreq = web.database(dbn='sqlite',db='./' + dbNameFreq)
        if newdb:
            self.dbFreq.query('''CREATE TABLE logs (
                word       TEXT,
                start      INT,
                end        INT,
                wordCount  INT,
                totalCount INT
                );''')

    def logFreq(self):

        N = self.freq.N()
        for key in self.keys:
            #put in db
            self.dbFreq.insert('logs',
                               word  = key,
                               start = self.start,
                               end   = self.end,
                               wordCount  = self.freq[key],
                               totalCount = N)
        
