"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

application = get_wsgi_application()


import socket, threading
import time, datetime, base64


logs=[];
channel = "#opencv"
nick = 'cv2'


def now():
    d = datetime.datetime.now().strftime("%d_%m_%Y")
    t = datetime.datetime.now().strftime("%H:%M:%S")
    return d,t

class IrcThread( threading.Thread ):
    def __init__(self):
        threading.Thread.__init__(self)

    def __del__(self):
        self.closeRegistry()

    def run( self ):
        #
        # main
        #
        try:
            # yikes SASL identification ..
            b64auth = base64.b64encode(nick+"\x00"+nick+"\x00"+"i_am_"+nick)
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect(('irc.freenode.net', 6667))
            irc.send("CAP REQ :sasl\r\n")
            irc.send("NICK " + nick + "\r\n")
            irc.send("USER " + nick + " 12 * :"+nick+"\r\n")
            m = irc.recv(512)
            if m.find("ACK :sasl"):
                irc.send("AUTHENTICATE PLAIN\r\n")
                irc.send("AUTHENTICATE "+b64auth+"\r\n")
                irc.send("CAP END\r\n")
            else:
                irc.send("PASS i_am_" + nick + "\r\n")
            irc.send("JOIN " + channel + "\r\n")

        except : pass # ?? (i forgot how to do exception handliing in py3)
        print("started irc",irc,channel,nick)
        while irc != None:
            m = irc.recv(512)
            if len(m)==0 or m == "\r\n":
                continue
            #print(m)
            if m.find("PING") == 0:
                irc.send("PONG 12345\r\n")

            me = m[1:m.find('!')] # whoo sent the msg
            targ = channel # where *was* it sent to
            to = channel # where *should* it go to now.
            pm = m.find("PRIVMSG %s :" % channel)
            if pm<0:
                pm = m.find("PRIVMSG %s :" % nick)
                to = nick
            if pm > 0:
                d,t = now()
                txt = m[pm+10+len(to):-2]
                if txt.find(".last") == 0:
                    for l in logs:
                        msg =  "PRIVMSG %s : %s\r\n" % (me, l)
                        irc.send(msg)
                        time.sleep(1) # actually, the "flood limit" is 2 seconds on freenode, but for 25 msgs, we'll fly under the radar
                    irc.send("PRIVMSG %s : that's it.\r\n" % me)
                else:
                    if targ == channel: # don't log cv2
                        line = "[%s] %s:\t%s" % (t,me,txt)
                        logs.append(line)
                        if len(logs) > 25:
                            del logs[0]
        irc.close()

# it only needs a seperate thread for running on paas ! (else the run() method() would be the whole application.)
t1 = IrcThread()
t1.start()
