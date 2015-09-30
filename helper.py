import cStringIO
import subprocess
import time
import ethtool
import sys
from smbus import SMBus

def GetAlt():
    #get the altitude from the MPL3115a2 device
    print "GetAlt()"
    #logfile.write("5")
    #sudo sh -c " echo -n 1 > /sys/module/i2c_bcm2708/parameters/combined"

    #subprocess.call(["sudo sh -c ""echo -n 1 > /sys/module/i2c_bcm2708/parameters/combined"" "], shell=True)

    #subprocess.call(["./enAlt"])
    
    #device address and register addresses
    altAddress = 0x60
    ctrlReg1 = 0x26
    ptDataCfg = 0x13

    #values
    oversample128 = 0x38
    oneShot= 0x02
    altMode = 0x80
    
    bus = SMBus(1)
    #logfile.write("6")
    for i in range(0,5):
        whoAmI = bus.read_byte_data(altAddress, 0x0c)
        if whoAmI == 0xc4:
            break
        elif i == 4:
            #logfile.write("fi")
            sys.exit()
        else:
            time.sleep(0.5)
    bus.write_byte_data(altAddress, ptDataCfg, 0x07)        
    #logfile.write("7")    

    oldSetting = bus.read_byte_data(altAddress, ctrlReg1)
    #logfile.write("7a")
    #time.sleep(1)
    newSetting = oldSetting | oversample128 | oneShot | altMode
    #logfile.write("7b")
    #time.sleep(1)
    bus.write_byte_data(altAddress, ctrlReg1, newSetting)

    #logfile.write("8")
    #event flags
    #bus.write_byte_data(altAddress, ptDataCfg, 0x07)
    #logfile.write("9")
    status = bus.read_byte_data(altAddress, 0x00)
    while(status & 0x08) ==0:
        status = bus.read_byte_data(altAddress, 0x00)
        time.sleep(0.5)
    #logfile.write("10")
    msb, csb, lsb = bus.read_i2c_block_data(altAddress, 0x01, 3)
    #logfile.write("11")
    alt = ((msb<<24) | (csb<<16) | (lsb<<8)) / 65536.
    #logfile.write("12")
    if alt > (1<<15):
        alt -= 1<<16
    #logfile.write("13")
    
    return alt
    
    


def ResetTime():
    #update the clock 
    subprocess.call(["sudo", "service", "ntp", "restart"])

def ResetGps():
    #kill the daemon to make sure everything is running clean
    print "ResetGps()"
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
    
