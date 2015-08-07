#SignalLogger.py - to run on Raspberry Pi B+ on startup and log 4G signal data from a connected netgear 785s wifi modem.
# - written for Python2.7
# - extra python packages via RPi apt-get:
#       python-lxml
#       python-requests
#       python-ethtool
# - extra python packages via pip:
#       speedtest-cli
# - autorun implemented by cron using:
#        crontab -e
#   then adding:
#       @reboot python /home/pi/Desktop/signalLogger.py

import lxml.html
import requests
import sys
import os
import speedtest_cli
import subprocess
import cStringIO
import datetime
import ethtool
import time

def GetSigData(loggedInCookie):
    #get signal data from 785S homepage
    targetUrl = "http://192.168.1.1/index.html"    
    homePage = requests.get(targetUrl, cookies = loggedInCookie)
    doc = lxml.html.fromstring(homePage.text)
    altitude = "##TODO##"
    rsrp = doc.find_class('m_wwan_signalStrength_rsrp')[0].text
    rsrq = doc.find_class('m_wwan_signalStrength_rsrq')[0].text
    
    #store original stdout so that it can be restored         
    oldStdOut = sys.stdout

    #create an alternate stream to divert stdout into
    speedTestOutput = cStringIO.StringIO()    
    sys.stdout= speedTestOutput    

    #run speedtest with simple argument by manually altering argv, storing data in alternate stdout
    sys.argv = [sys.argv[0], '--simple']
    speedtest_cli.speedtest()

    #reset stdout to original 
    sys.stdout = oldStdOut
    
    speeds = speedTestOutput.getvalue()
    speedSplit = speeds.split("\n")
    upSpeed = speedSplit[2].split(" ")[1]
    downSpeed = speedSplit[1].split(" ")[1]
    ping = speedSplit[0].split(" ")[1]
    droppedPackets = "##TODO"
    logline = altitude + "," + rsrp + "," + rsrq + "," + upSpeed + "," + downSpeed + "," + ping + "," + droppedPackets + "\n"
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
    if not os.path.isdir('/home/pi/Desktop/droneLogs'):
        os.makedirs('/home/pi/Desktop/droneLogs')
    lognumber = 0    
    logfileName = '/home/pi/Desktop/droneLogs/logfile0.log'
    while os.path.isfile(logfileName):
        lognumber += 1
        logfileName = '/home/pi/Desktop/droneLogs/logfile' + str(lognumber) + '.log'
    logFile = open(logfileName , 'w')
    
    #timestamp the logfile (maybe put this in filename)
    logFile.write(str(datetime.datetime.now()) + "\n")
    logFile.write("altitude,rsrp,rsrq,upSpeed,downSpeed,ping,droppedPackets\n")
    return logFile

def main():
    
    try:
        #turn on the internet and check it's connected
        subprocess.call(["sudo", "dhclient", "eth1"])
        if not "eth1" in ethtool.get_active_devices():
            print "error: eth1 connection is not working"
 
        #update the clock 
        call(["sudo", "service", "ntp", "restart"])

        #wait for time to update
        time.sleep(10)
        
        sessionCookie = Login()
        logFile = OpenLogFile()
        for x in range(0,1):
            logFile.write(GetSigData(sessionCookie))
            #print GetSigData(sessionCookie)
        print "done"
    except:
        print "login problem: ", sys.exc_info()[0]

if __name__ == "__main__":
    main()
