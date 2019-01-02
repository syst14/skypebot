import tweepy
from tweepy import OAuthHandler

'''
your twitter api credentials
'''
consumer_key = 'YOUR_CONSUMER_KEY'
consumer_secret = 'YOUR_CINSUMER_SECRET'
access_token = 'YOUR_ACCESS_TOKEN'
access_secret = 'YOUR_ACCESS_SECRET'


def twitter(usr):
    '''
    last tweet by user name returner
    '''
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api  = tweepy.API(auth)
    res  = api.user_timeline(id = str(usr), count=1)
    tweet_txt  = res[0].text.encode('utf-8')
    tweet_link = 'https://twitter.com/'+usr+'/status/'+res[0].id_str
    return tweet_txt, tweet_link
