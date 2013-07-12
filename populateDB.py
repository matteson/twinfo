from classes import TwitterLogFromStream
from classes import Authorize

auth = Authorize('authStore.db')
auth_dict = auth.getData('my_app')

stream = TwitterLogFromStream(False,'corpusTweets.db',
                    auth_dict['APP_KEY'],
                    auth_dict['APP_SECRET'],
                    auth_dict['OAUTH_TOKEN'],
                    auth_dict['OAUTH_TOKEN_SECRET'])
stream.statuses.filter(track='the',language='en')
