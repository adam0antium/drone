#SignalLogger.py - to run on Raspberry Pi B+ on startup and log 4G signal data from a connected netgear 785s wifi modem.
# - written for Python2.7
# - extra python packages via RPi apt-get:
#       python-lxml
#       python-requests
# - autorun implemented by cron using:
#        crontab -e
#   then adding (without line breaks):
#       @reboot sudo dhclient eth1
#       && sleep 10 && /home/pi/Desktop/drone/enAlt.sh
#       && sleep 10 && sudo python /home/pi/Desktop/drone/signalLogger.py &
#

from smbus import SMBus
import lxml.html
import requests
import sys
import os
import subprocess
import cStringIO
import datetime
import ethtool
import time
import threading
import RPi.GPIO as gpio

def QuickSpeedTest():
    #a much faster executing, but less accurate speedtest
    print "QuickSpeedTest()"
    #the telstra hosted speedtest site, corresponding to speedtest
    #   server 2225
    telstraTestUrl = "http://mel1.speedtest.telstra.net/speedtest/"

    #one of a number of files hosted on the server this one ~2MB
    #   for others try dimensions 500,1500,2000,2500,3000,3500,4000
    downloadFileName = "random1000x1000.jpg"

    dlSpeedString = subprocess.check_output(["curl", telstraTestUrl
        + downloadFileName, "-o", "this.jpg", "--silent", "-w"
        , "%{speed_download}", "-m", "10"])
      
    ulSpeedString = subprocess.check_output(["curl", "-T", "this.jpg"
        , "-o", "/dev/null", telstraTestUrl + "upload.php", "-w"
        , "%{speed_upload}", "--silent", "-m", "10"])

    pingString = subprocess.check_output(["ping", "203.39.77.13"
        , "-c", "3", "-q"])
    
    #get the average round trip ping time
    latencyString = pingString.split("/")[4]
    packetsReceivedStr = pingString.split(",")[1]
    packetsReceivedStr = packetsReceivedStr.split(" ")[1]
    
    packetsReceived = int(packetsReceivedStr)
    latency = float(latencyString)
    downloadSpeed = float(dlSpeedString)
    uploadSpeed = float(ulSpeedString)

    return {'downloadSpeed': downloadSpeed, 'uploadSpeed': uploadSpeed
        , 'latency': latency, 'packetsReceived': packetsReceived}

def GetAlt():
    #get the altitude from the MPL3115a2 device
    print "GetAlt()"
    
    #device address and register addresses
    altAddress = 0x60
    ctrlReg1 = 0x26
    ptDataCfg = 0x13

    #values
    oversample128 = 0x38
    oneShot= 0x02
    altMode = 0x80
    
    bus = SMBus(1)
    for i in range(0,5):
        whoAmI = bus.read_byte_data(altAddress, 0x0c)
        if whoAmI == 0xc4:
            break
        elif i == 4:
            sys.exit()
        else:
            time.sleep(0.5)
    bus.write_byte_data(altAddress, ptDataCfg, 0x07)        

    oldSetting = bus.read_byte_data(altAddress, ctrlReg1)

    newSetting = oldSetting | oversample128 | oneShot | altMode
   
    bus.write_byte_data(altAddress, ctrlReg1, newSetting)

    status = bus.read_byte_data(altAddress, 0x00)
    while(status & 0x08) ==0:
        status = bus.read_byte_data(altAddress, 0x00)
        time.sleep(0.5)
    msb, csb, lsb = bus.read_i2c_block_data(altAddress, 0x01, 3)
    alt = ((msb<<24) | (csb<<16) | (lsb<<8)) / 65536.
    if alt > (1<<15):
        alt -= 1<<16
    
    return alt    

class LedThreader(threading.Thread):
    #class to handle the blinking LED for altitude information
    def __init__(self):
        threading.Thread.__init__(self)
        gpio.setmode(gpio.BOARD)
        gpio.setup(11, gpio.OUT)
        gpio.output(11, gpio.LOW)
        self.isThreadCancelled = False
        self.setDaemon(True)
        
    def run(self):
        try:
            isLedOn = False
            while True:
                if self.isThreadCancelled:
                    gpio.output(11, gpio.LOW)
                    
                    break
                if isLedOn:
                    gpio.output(11, gpio.LOW)
                    
                    isLedOn = False
                else:
                    gpio.output(11, gpio.HIGH)
                    isLedOn =True
                time.sleep(0.25)
        except StopIteration:
            pass
        
    def stop(self):
        self.isThreadCancelled = True
        gpio.cleanup()
        
def GetSigData(loggedInCookie):
    #get signal data. Argument is cookie of admin-logged-in homepage.
    print "GetSigData()"
    
    #this is the logged in webpage, which contains all data in the raw
    #   html, despite the presentation tabs
    targetUrl = "http://192.168.1.1/index.html"
   
    homePage = requests.get(targetUrl, cookies = loggedInCookie, timeout=1)
   
    doc = lxml.html.fromstring(homePage.text)
   
    altitude = str(GetAlt())
   
    rsrp = doc.find_class('m_wwan_signalStrength_rsrp')[0].text
    rsrq = doc.find_class('m_wwan_signalStrength_rsrq')[0].text
   
    speeds = QuickSpeedTest()
    downSpeed = str(speeds['downloadSpeed'])
    upSpeed = str(speeds['uploadSpeed'])
    pingTime = str(speeds['latency'])
    packetsReceived = str(speeds['packetsReceived'])
    
    logline = (altitude + "," + rsrp + "," + rsrq + "," + upSpeed + ","
        + downSpeed + "," + pingTime + "," + packetsReceived + "\n")

    print logline
    
    return logline
            
def Login():
    #login to 785S homepage as admin (settings data is only available as admin)
    print "Login()"
    targetUrl = "http://192.168.1.1/index.html"
    configFormUrl = "http://192.168.1.1/Forms/config"
    unAuthResponse = requests.get(targetUrl, timeout=1)
    sessionCookie = unAuthResponse.cookies

    #pulled this post data format from the Telstra Challenge github repo 
    secToken = sessionCookie['sessionId'].split('-')[1]

    postData = ("token=" + secToken + "&ok_redirect=%2Findex.html"
        "&err_redirect=%2Findex.html&session.password=admin")

    requests.post(configFormUrl, cookies = sessionCookie,
                  data = postData, timeout=1)

    return sessionCookie

def CreateLogFile():
    #set up the log file for writing to
    print "OpenLogFile()"
    if not os.path.isdir('/home/pi/Desktop/droneLogs'):
        os.makedirs('/home/pi/Desktop/droneLogs')
    lognumber = 0    
    logfileName = '/home/pi/Desktop/droneLogs/logfile0.log'
    while os.path.isfile(logfileName):
        lognumber += 1
        logfileName = ('/home/pi/Desktop/droneLogs/logfile' + str(lognumber)
            + '.log')
    logFile = open(logfileName , 'w')
    
    #timestamp the logfile with UTC (maybe put this in filename) 
    logFile.write(str(datetime.datetime.now()) + "\n")

    #logFile.write(localTime)
    logFile.write("altitude,rsrp,rsrq,upSpeed,downSpeed,ping,droppedPackets\n")
    logFile.close()
    return logfileName

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
   
    logFileName = CreateLogFile()
    logFile = open(logFileName, 'a')
    logFile.close()
    while(True):
        try:
            out = GetSigData(sessionCookie)
        except:
            logFile = open(logFileName, 'a')
            logFile.write(sys.exc_info()[0])
            sys.exit()
        logFile = open(logFileName, 'a')        
        
        logFile.write(out)
        logFile.close()

def main():
    try:
        
        ledThread = LedThreader()
        ledThread.start()
        StartLogging()
        
    except:
        ledThread.stop()
        print "Exception thrown: ", sys.exc_info()[0]
        sys.exit()

if __name__ == "__main__":
    main()
