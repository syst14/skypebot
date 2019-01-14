import time
import requests
import json
from threading import Thread
from flask import request, Flask
from twitter import twitter
from bothelper import BotHelper
import redis

FLASK = Flask(__name__)
APP_ID = 'YOUR_APP_ID'
PASSWORD = 'YOUR_PASSWORD'
OWM_API = 'YOUR_OWM_KEY'
context =('/etc/letsencrypt/archive/www.avitiuk.space/fullchain1.pem', '/etc/letsencrypt/archive/www.avitiuk.space/privkey1.pem')
TOKEN = {}
GAMEMODE = []
NOTIFY = []

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
    return j['access_token']

def weather():
    '''
    get, store and diff tempreture
    '''
    location = 'kiev' #defination for further extensibility 
    try:
        q = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}'.format(location,OWM_API)).content
        j =  json.loads(str(q))
        new_temp = j['main']['temp']
    except Exception as e:
        print "latest wether data request failure"
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    old_temp = float(r.get('weather')) #predefined redis key with start parameter
    if new_temp != old_temp:
        r.set('weather',new_temp)
        weather_handler(new_temp) #call notification with update

def weather_handler(temp):
    '''
    send tempreture chats with enabled notifications
    '''
    for convs in NOTIFY:
        data = BotHelper.data_formatter({},convs)
        helper = BotHelper(data, TOKEN['access_token'])
        temp_upd = helper.tocelsium(temp)
        notification_msg = "Latest update regarding wheather, current tempreture is {} now!".format(temp_upd)
        helper.add_text(notification_msg)
        helper.sender()

def get_and_verify_token():
    '''
    token refresher and weather monitoring in one thread
    '''
    global TOKEN
    while True:
        get_token()
        weather()
        time.sleep(TOKEN['expires_in']*0.9)


@FLASK.route('/', methods=['POST'])
def handle():
    '''
    main function with logic and some handlers
    '''
    global GAMEMODE
    global NOTIFY
    data = request.get_json()
    if not data.get('text'):
        #logic for no message request
        data.update({"text":""})
        #return 'success'
    helper = BotHelper(data, TOKEN['access_token'])
    payload = helper.payload
    '''
    switcher to activate\deactivate gamemode (input message lenth counter)
    and conversation with weather notification
    '''
    if '#start' in data['text'].lower():
        GAMEMODE.append(data['conversation']['id'])
        return 'success'
    elif '#stop' in data['text'].lower():
        try:
            GAMEMODE.remove(data['conversation']['id'])
        except ValueError:
            print 'Invalid gamemode action'
    elif '#notify' in data['text'].lower():
        NOTIFY.append(data['conversation']['id'])
        print '@@@ this conv enabled notification -----> ' + data['conversation']['id']
        return 'success'
    elif '#offnotify' in data['text'].lower():
        try:
            NOTIFY.remove(data['conversation']['id'])
        except ValueError:
            print 'Invalid notify mode action'
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

@FLASK.route('/msg/sender', methods=['POST'])
def rest_sender():
    '''
    sendig messages with REST API call
    '''
    input_data = request.get_json()
    print input_data
    if not input_data.get('conversation').get('id') or not input_data.get('text'):
        return 'bad request' #400 
    data = BotHelper.data_formatter({},input_data['conversation']['id'])
    helper = BotHelper(data, TOKEN['access_token'])
    helper.add_text(input_data['text'])
    helper.sender()
    return 'success'

@FLASK.route('/msg/notify', methods=['GET'])
def notify_test():
    '''
    manual notification send
    '''
    weather_handler(999)
    return 'success'

if __name__ == '__main__':
    thread = Thread( target=get_and_verify_token )
    thread.start()
    FLASK.run(host='0.0.0.0', port=8888, ssl_context=context)

