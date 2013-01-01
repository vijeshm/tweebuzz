'''
import tweepy

consumer_key = "x0NZFq1vnR2RxdwVh0Tg"
consumer_secret = "pBLWNFbFoUp8I8AU9T2odW1wKhaUSleplxBzcC9thV4"
access_token = "258012996-S6wBDJyZcQCCa7mldPrHokNjIW8orIcL9aa6zUjQ"
access_secret = "5YZjf6dsyONdajfHbZPQdgkTA8YWcgJONfMj0grEc"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)
print api.me().name
print "Hello"
'''

import tweepy
consumer_key = 'rOpYjZTYVIYYTxh3TIw'
consumer_secret = 'Cq5rT7Qqy7pmIMhEjWlgBUfdJYc68pTukSFbT57c4'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#auth_url = "https://api.twitter.com/oauth/authorize"
auth_url = auth.get_authorization_url()
print 'Please authorize: ' + auth_url
verifier = raw_input('PIN: ').strip()
auth.get_access_token(verifier)
print "ACCESS_KEY = '%s'" % auth.access_token.key
print "ACCESS_SECRET = '%s'" % auth.access_token.secret