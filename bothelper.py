import re
import requests
import json

class BotHelper():
    def __init__(self, data,    #type: mapping
                token           #type: string
                ):
        self.data  = data
        self.token = token
        self.payload = {
            "type": "message",
            "from": {
                    "id": self.data['recipient']['id'],
                    "name": "skybot-avitiuk"
                },
            "conversation": {
                "id": self.data['conversation']['id']
                }
        }

    def sender(self):
        '''
        requestes to bot framework api sender
        '''
        url = self.data['serviceUrl'] + '/v3/conversations/{}/activities/'.format(self.data['conversation']['id'])
        headers = {'Authorization': 'Bearer ' + self.token,
                   'content-type': 'application/json; charset=utf8'}
        requests.post(url, headers=headers, data=json.dumps(self.payload))
        try:
            #text cleaner
            del self.payload['text']
        except KeyError:
            print 'payload text clean unsuccessful'

    def add_text(self, text):
        self.payload.update({"text":text})

    def msg_len_updater(self):
        self.payload.update({"text": "Your message consist of " + str(len(self.data['text'].replace(' ','').strip())) + " symbols"})

    def perm(self):
        if re.search('playtika',self.data['text'].lower()):
            self.payload.update({"text":"Oh, you are playtikan? Cool!"})
            return True

    def twitter_usr(self):
        usr = re.findall('@\w+', self.data['text'])
        if len(usr) > 0:
            return str(usr[0].strip()).lower()