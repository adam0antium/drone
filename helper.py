import subprocess
import time
import ethtool

def ResetTime():
    #update the clock 
    subprocess.call(["sudo", "service", "ntp", "restart"])

def ResetGps():
    #kill the daemon to make sure everything is running clean
    subprocess.call(["sudo", "killall", "gpsd"])
    time.sleep(1)

    #restart the daemon
    subprocess.call(["sudo", "gpsd", "/dev/ttyUSB0", "-F", "/var/run/gpsd.sock"])

def CheckInternet():
    #turn on the internet and check it's connected
    if not "eth1" in ethtool.get_active_devices():
        print "error: eth1 connection is not working"
    else:
        print "connection oK"
