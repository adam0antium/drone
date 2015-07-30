#SignalLogger.py - to run on Raspberry Pi B+ on startup and log 4G signal data from a connected netgear 785s wifi modem.
# - written for Python2.7
# - extra python packages via RPi apt-get:
#       python-lxml
#       python-requests
# - extra python packages via pip:
#       speedtest-cli
# - autorun implemented by cron using:
#        crontab -e
#   then adding:
#       @reboot python /home/pi/Desktop/signalLogger.py

from lxml.html import fromstring
import requests
import sys
import os
import speedtest_cli


  
def GetSigData(loggedInCookie):
    targetUrl = "http://192.168.1.1/index.html"    
    homePage = requests.get(targetUrl, cookies = loggedInCookie)
    doc = fromstring(homePage.text)
    logline = "4G/LTE data:" \
        + "    RSRP: " \
        + doc.find_class('m_wwan_signalStrength_rsrp')[0].text \
        + "    RSRQ: " \
        + doc.find_class('m_wwan_signalStrength_rsrq')[0].text \
        + "\n"
    return logline
            
def Login():
    targetUrl = "http://192.168.1.1/index.html"
    configFormUrl = "http://192.168.1.1/Forms/config"
    unAuthResponse = requests.get(targetUrl)
    sessionCookie = unAuthResponse.cookies

    #pulled this post data format from the Telstra Challenge github repo 
    secToken = sessionCookie['sessionId'].split('-')[1]
    postData = "token=" + secToken + "&ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password=admin"
    
    requests.post(configFormUrl, cookies = sessionCookie, data = postData)
    return sessionCookie

def OpenLogFile():
    lognumber = 0    
    logfileName = 'logfile0.log'
    while os.path.isfile(logfileName):
        lognumber += 1
        logfileName = '/home/pi/Desktop/logfile' + str(lognumber) + '.log'
    logFile = open(logfileName , 'w')
    #timestamp the logfile (maybe put this in filename)
    from datetime import datetime
    logFile.write(str(datetime.now()) + "\n")
    logFile.write("altitude,rsrp,rsrq,upSpeed,downSpeed,ping,droppedPackets\n")
    return logFile

def main():
    
    try:
        from subprocess import call
        #turn on the internet
        call(["sudo", "dhclient", "eth1"])
        #update the clock (not sure if this is effective)
        call(["sudo", "service", "ntp", "restart"])
        sessionCookie = Login()
        logFile = OpenLogFile()
        for x in range(0,1):
            logFile.write(GetSigData(sessionCookie))
            print GetSigData(sessionCookie)
 #           sys.argv = [sys.argv[0], '--simple']
 #           print speedtest_cli.speedtest()
    except:
        print "login problem: ", sys.exc_info()[0]

if __name__ == "__main__":
    main()
