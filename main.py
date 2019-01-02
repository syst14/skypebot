
import time
import requests
import json
from threading import Thread
from flask import request, Flask
from twitter import twitter
from bothelper import Bothelper

FLASK = Flask(__name__)
APP_ID = 'YOUR_APP_ID'
PASSWORD = 'YOUR_PASSWORD'
context =('/etc/letsencrypt/archive/www.avitiuk.space/fullchain1.pem', '/etc/letsencrypt/archive/www.avitiuk.space/privkey1.pem')
TOKEN = {}
GAMEMODE = []


def get_token():
    '''
    token getter function
    '''
    global TOKEN
    payload = {'grant_type': 'client_credentials',
               'client_id': APP_ID,
               'client_secret': PASSWORD,
               'scope': 'https://api.botframework.com/.default',
              }
    token = requests.post('https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token', data=payload).content
    j = json.loads(str(token))
    try:
      del j['token_type'],j['ext_expires_in']
    except KeyError:
      print "Reply from Skype API changed, please review get_token()"
      #could be any type of notification
    TOKEN = j
    return j

def get_and_verify_token():
    '''
    token refresher
    '''
    global TOKEN
    while True:
        get_token()
        time.sleep(TOKEN['expires_in']*0.9)


@FLASK.route('/', methods=['GET', 'POST'])
def handle():
    '''
    main function with logic and some handlers
    '''
    global GAMEMODE
    data = request.get_json()
    if not data.get('text'):
        #logic for no message request
        return 'success'
    helper = Bothelper(data, TOKEN['access_token'])
    payload = helper.payload
    '''
    switcher to activate\deactivate gamemode (input message lenth counter)
    '''
    if '#start' in data['text'].lower():
        GAMEMODE.append(data['conversation']['id'])
        return 'success'
    elif '#stop' in data['text'].lower():
        try:
            GAMEMODE.remove(data['conversation']['id'])
        except ValueError:
            print 'Invalid gamemode action'
    else:
        pass

    '''
    permanent check of ALL messages 
    '''
    if helper.perm():
        helper.sender()
    
    if data.get('isGroup'):
        '''
        block for Group chat
        '''
        return 'succes'
    '''
    block for private chat
    '''
    if data['id'][-4:] == '0000' or data.get('membersAdded') or '#init' in data['text'].lower():
        #bot's greetings
        helper.add_text('Hello Human (wave)')
        helper.sender()
        twitter_start = 'Do you follow my creator\'s twitter? Here is his last tweet: {}. Link: {} \n I can show you ' \
                        'last tweet for any of users. Just type me a user name like @slotomania \n' \
                        'I can play with you a very simple game. I will count your message length. Cool, yeah? \n ' \
                        'Type #start or #stop to start or stop game accordingly.'
        tweet_txt, tweet_link = twitter('ar4i_ua')
        helper.add_text(twitter_start.format(tweet_txt,tweet_link))
        helper.sender()
    elif data['conversation']['id'] in GAMEMODE:
        #working on game reply 
        helper.msg_len_updater()
        helper.sender()
    else:
        #reply to recieved valid twitter user name
        usr = helper.twitter_usr()
        if usr:
            tweet_txt, tweet_link = twitter(usr)
            twitter_res = 'Last tweet of user {}: {} \nLink: {}'
            helper.add_text(twitter_res.format(usr, tweet_txt, tweet_link))
            helper.sender()
        else:
            pass

    return 'success'


if __name__ == '__main__':
    thread = Thread( target=get_and_verify_token )
    thread.start()
    FLASK.run(host='0.0.0.0', port=8888, ssl_context=context)

