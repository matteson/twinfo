from classes import TwitterLogFromQuery
from classes import TwitterLogFromStream
from classes import Authorize
import time

auth = Authorize('authStore.db')
auth_dict = auth.getData('my_app')

##while True:
##    currStartTime = time.time()
##    timeout = 300
##    stream = TwitterLogFromStream(False,'corpusTweetsPractice.db',
##                                  currStartTime+timeout, # gather for 5 min
##                        auth_dict['APP_KEY'],
##                        auth_dict['APP_SECRET'],
##                        auth_dict['OAUTH_TOKEN'],
##                        auth_dict['OAUTH_TOKEN_SECRET'])
##    stream.statuses.filter(track='the',language='en')

currStartTime = time.time()
timeout = 600
stream = TwitterLogFromQuery(False,'beerwine.db',['beer','wine'],
                    auth_dict['APP_KEY'],
                    auth_dict['APP_SECRET'],
                    auth_dict['OAUTH_TOKEN'],
                    auth_dict['OAUTH_TOKEN_SECRET'])
stream.beginQuery()

