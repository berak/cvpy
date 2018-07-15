import io, os, sys, socket, threading, subprocess
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
            #irc.send("Nickserv identify i_am_cv2\r\n")
        except Exception,e: print(e)
        print("started irc",irc,channel,nick)
        while irc != None:
            m = irc.recv(512)
            if len(m)==0 or m == "\r\n":
                continue
            print m
            if m.find("PING") == 0:
                irc.send("PONG 12345\r\n")

            me = m[1:m.find('!')]
            targ = channel
            to = channel
            pm = m.find("PRIVMSG %s :" % channel)
            if pm<0:
                pm = m.find("PRIVMSG %s :" % nick)
                to = nick
            if pm > 0:
                d,t = now()
                d = "/" + d
                txt = m[pm+10+len(to):-2]
                if txt.find(".last") == 0:
                    for l in logs:
                        msg =  "PRIVMSG %s : %s\r\n" % (me, l)
                        irc.send(msg)
                        time.sleep(1)
                    irc.send("PRIVMSG %s : that's it.\r\n" % me)
                else:
                    if targ == channel: # don't log cv2
                        line = "[%s] %s:\t%s" % (t,me,txt)
                        logs.append(line)
                        if len(logs) > 25:
                            del logs[0]
        irc.close()


t1 = IrcThread()
t1.start()




def application(environ, start_response):
    data = "helo."
    start_response("200 OK", [
            ("Content-Type", "text/html"),
            ("Content-Length", str(len(data)))
            ])
    return iter([data])

from wsgiref.simple_server import make_server
httpd = make_server( '0.0.0.0', int(os.environ.get("PORT", 9000)), application )
while True: httpd.handle_request()
