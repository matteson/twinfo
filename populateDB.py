from classes import TwitterLogFromQuery
from classes import TwitterLogFromStream
from classes import Authorize
import time

auth = Authorize('authStore.db')
auth_dict = auth.getData('my_app')

##while True:
##
##    try:

currStartTime = time.time()
timeout = 600
stream = TwitterLogFromQuery(False,'generalSearch.db',['prochoice','prolife'],
                    auth_dict['APP_KEY'],
                    auth_dict['APP_SECRET'],
                    auth_dict['OAUTH_TOKEN'],
                    auth_dict['OAUTH_TOKEN_SECRET'])
stream.beginQuery()

##    except:
##        time.sleep(60)
