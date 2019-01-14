import sys
from bothelper import BotHelper
from main import get_token

APP_ID = 'YOUR_APP_ID'
PASSWORD = 'YOUR_PASSWORD'
exception_msg = 'Expected arguments: "bot-cli.py message conversationID,N...'

args = sys.argv
if len(args) == 3:
    token = get_token()
    for convs in args[-1].split(','):
        data = BotHelper.data_formatter({},convs.strip())
        helper = BotHelper(data, token)
        helper.add_text(str(args[1]))
        helper.sender()
    print 'messages sent'
else:
    print 'Expected arguments: "bot-cli.py message [conversationID,N...]'