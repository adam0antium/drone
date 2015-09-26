import cStringIO
import subprocess
import time
import ethtool
import sys

def ResetTime():
    #update the clock 
    subprocess.call(["sudo", "service", "ntp", "restart"])

def ResetGps():
    #kill the daemon to make sure everything is running clean
    subprocess.call(["sudo", "killall", "gpsd"])
    time.sleep(1)

    #restart the daemon
    subprocess.call(["sudo", "gpsd", "/dev/ttyUSB0", "-F",
                     "/var/run/gpsd.sock"])

def CheckInternet():
    #turn on the internet and check it's connected
    if not "eth1" in ethtool.get_active_devices():
        print "error: eth1 connection is not working"
    else:
        print "connection oK"

def QuickSpeedTest():
    #a much faster executing, but less accurate speedtest

    #the telstra hosted speedtest site, corresponding to speedtest
    #   server 2225
    telstraTestUrl = "http://mel1.speedtest.telstra.net/speedtest/"

    #one of a number of files hosted on the server this one ~2MB
    #   for others try dimensions 500,1500,2000,2500,3000,3500,4000
    downloadFileName = "random1000x1000.jpg"

    dlSpeedString = subprocess.check_output(["curl", telstraTestUrl
        + downloadFileName, "-o", "this.jpg", "--silent", "-w"
        , "%{speed_download}"])
      
    ulSpeedString = subprocess.check_output(["curl", "-T", "this.jpg"
        , "-o", "/dev/null", telstraTestUrl + "upload.php", "-w"
        , "%{speed_upload}", "--silent"])

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
    
