import re
import requests
import json

class Bothelper():
    def __init__(self, data,    #type: mapping
                token           #type: string
                ):
        self.data  = data
        self.token = token
        self.payload = {
            "type": "message",
            "from": {
                    "id": 'skybot-avitiuk@2kCf01tTXR0',
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
        if not self.data.get('serviceUrl'):
            self.data.update({'serviceUrl':'https://smba.trafficmanager.net/apis/'})
        url = self.data['serviceUrl'] + '/v3/conversations/{}/activities/'.format(self.data['conversation']['id'])
        headers = {'Authorization': 'Bearer ' + self.token,
                   'content-type': 'application/json; charset=utf8'}
        requests.post(url, headers=headers, data=json.dumps(self.payload))
        # print '--------MSG--------'
        # print self.payload['text']
        # print self.payload['conversation']['id']
        # print '------SENT-------'
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
    @staticmethod
    def tocelsium(temp):
        '''
        weather converter
        '''
        kelvin_const = -273.15
        celsium = str(float(temp) + kelvin_const)
        return celsium + u' \xb0C'.encode('utf8')
    @staticmethod
    def data_formatter(data, id):
        '''
        helper for out of chat input data
        '''
        data.update({"conversation":{"id":id}})
        return data