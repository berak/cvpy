import socket
import time, datetime, base64



def now():
    d = datetime.datetime.now().strftime("%d_%m_%Y")
    t = datetime.datetime.now().strftime("%H:%M:%S")
    return d,t


def run_bot():
    logs=[];
    channel = "#opencv"
    nick = 'cvtail'
    maxn = 100
    ntail = 25

    #
    # main
    #
    # yikes, SASL identification ..
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
    print("started irc",irc,channel,nick)

    mc=0
    while irc != None:
        m = irc.recv(512)
        if not m:
            break
        if len(m)==0 or m == "\r\n":
            continue
        if mc < 60: print(m)
        mc += 1
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
            if txt.find(".clear") == 0:
                logs=[]
                msg =  "PRIVMSG %s : ok.\r\n" % (me,)
                irc.send(msg)
                continue
            if txt.find(".size") == 0:
                msg =  "PRIVMSG %s : %d.\r\n" % (me,len(logs))
                irc.send(msg)
                continue

            istail = (txt.find(".tail") == 0)
            ishead = (txt.find(".head") == 0)
            if istail or ishead:
                tt = txt.split(" ")
                nt = ntail
                if len(tt) > 1:
                    try: nt = int(tt[1])
                    except: pass
                if istail:
                    off = max(len(logs) - nt, 0)
                    li = logs[off:]
                else:
                    off = min(len(logs),nt)
                    li = logs[:off]
                c=0
                for l in li:
                    c += 1
                    msg =  "PRIVMSG %s : %s\r\n" % (me, l)
                    irc.send(msg)
                    time.sleep(1) # actually, the "flood limit" is 2 seconds on freenode, but for 25 msgs, we'll fly under the radar
                irc.send("PRIVMSG %s : %d msg.\r\n" % (me,c))
            else:
                if targ != nick: # don't log cv2
                    line = "[%s] %s:\t%s" % (t,me,txt)
                    logs.append(line)
                    if len(logs) > maxn:
                        del logs[0]
                    #print(len(logs), line)
    irc.close()

if __name__ == '__main__':
    while(True):
        run_bot()
