from classes import TwitterLogFromQuery
from classes import TwitterLogFromStream
from classes import Authorize
import time

auth = Authorize('authStore.db')
auth_dict = auth.getData('my_app')

currStartTime = time.time()
timeout = 300
stream = TwitterLogFromStream(True,'corpusTweets.db',
                              [],float('inf'), 
                    auth_dict['APP_KEY'],
                    auth_dict['APP_SECRET'],
                    auth_dict['OAUTH_TOKEN'],
                    auth_dict['OAUTH_TOKEN_SECRET'])
stream.statuses.sample(language='en')



