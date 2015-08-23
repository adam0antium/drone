#SignalLogger.py - to run on Raspberry Pi B+ on startup and log 4G signal data from a connected netgear 785s wifi modem.
# - written for Python2.7
# - extra python packages via RPi apt-get:
#       python-lxml
#       python-requests
#       python-ethtool
#       python-gps
#       (python-pip)
# - extra python packages via pip:
#       speedtest-cli
# - extra external packages:
#       gpsd
#       gpsd-clients
# - autorun implemented by cron using:
#        crontab -e
#   then adding:
#       @reboot python /home/pi/Desktop/signalLogger.py
# - to start gps stuff:
#       $ sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
# - to check gps is running:
#       $ cgps -s
# - if gps throws timeout error restart by:
#       $ sudo killall gpsd
#   and redo above gpsd command to start.
#

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

#gps stuff, not sure why this doesn't work when I do 'import gps' then add 'gps.' to commands, should be equivalent
from gps import *
import threading

class GpsThreader(threading.Thread):
    #class to handle the gps data-updating thread. 
    def __init__(self):
        threading.Thread.__init__(self)
        self.gpsWatcher = gps(mode=WATCH_ENABLE)
        self.data = None
        self.gpsWatcher.next()

    def getData(self):
        return self.data
    
    def run(self):
        try:
            while True:
                self.data = self.gpsWatcher.next()
            #a pause here might be good, depending on how quickly the gps is updating. Constant fetching may be unnecessary.
                #time.sleep(5)
        except StopIteration:
            pass
                
def InitiateGps():
    #initiate a new thread to keep track of latest gps data
    print "IntitateGps()"
    subprocess.call(["sudo", "killall", "gpsd"])
    time.sleep(1)
    subprocess.call(["sudo", "gpsd", "/dev/ttyUSB0", "-F", "/var/run/gpsd.sock"])
    time.sleep(1)
    gpsThread = GpsThreader()
    gpsThread.start()
    return gpsThread
    
def GetAltitude(gpsThread):
    #get the current altitude value from the gps thread.
    print "GetAltitude()"
    out = gpsThread.getData()
    if out != None:
        return str(out.get('alt'))   

def GetSigData(loggedInCookie, gpsThread):
    #get signal data. Argument is cookie of admin-logged-in homepage.
    print "GetSigData()"
    targetUrl = "http://192.168.1.1/index.html"
    print "1"
    homePage = requests.get(targetUrl, cookies = loggedInCookie)
    doc = lxml.html.fromstring(homePage.text)
    altitude = GetAltitude(gpsThread)
    rsrp = doc.find_class('m_wwan_signalStrength_rsrp')[0].text
    rsrq = doc.find_class('m_wwan_signalStrength_rsrq')[0].text
    print "2"
    #store original stdout so that it can be restored         
    oldStdOut = sys.stdout
    print "22"
    #create an alternate stream to divert stdout into
    speedTestOutput = cStringIO.StringIO()    
    print "222"
    sys.stdout= speedTestOutput    
    #run speedtest with simple argument by manually altering argv, storing data in alternate stdout
    sys.argv = [sys.argv[0], '--simple']
    speedtest_cli.speedtest()
    #reset stdout to original 
    sys.stdout = oldStdOut
    print "5"
    speeds = speedTestOutput.getvalue()
    print "6"
    speedSplit = speeds.split("\n")
    print "7"
    print speedSplit
    upSpeed = speedSplit[2].split(" ")[1]
    downSpeed = speedSplit[1].split(" ")[1]
    ping = speedSplit[0].split(" ")[1]
    droppedPackets = "##TODO"

    logline = altitude + "," + rsrp + "," + rsrq + "," + upSpeed + "," + downSpeed + "," + ping + "," + droppedPackets + "\n"
    print "5"
    return logline
            
def Login():
    #login to 785S homepage as admin (settings data is only available as admin)
    print "Login()"
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
    #set up the log file for writing to
    print "OpenLogFile()"
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

def ResetTime():
    #update the clock 
    print "ResetTime()"
    subprocess.call(["sudo", "service", "ntp", "restart"])
    #wait for time to update
    time.sleep(10)

def CheckInternet():
    #turn on the internet and check it's connected
    print "CheckInternet()"
    subprocess.call(["sudo", "dhclient", "eth1"])
    if not "eth1" in ethtool.get_active_devices():
        print "error: eth1 connection is not working"
        sys.exit(1)

def StartLogging():
    #looping logging function
    print "StartLogging()"
    sessionCookie = Login()
    gpsThread = InitiateGps()
    logFile = OpenLogFile()
    for x in range(0,5):
        logFile.write(GetSigData(sessionCookie, gpsThread))

def main():
    #print "main"
    try:
        CheckInternet()
        ResetTime()
        StartLogging()
    except:
        print "Exception thrown: ", sys.exc_info()[0]
        subprocess.call(["sudo", "killall", "gpsd"])

if __name__ == "__main__":
    main()
