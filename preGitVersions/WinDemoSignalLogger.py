import re
import sys
import time
import urllib2
import urllib
import cookielib
from bs4 import BeautifulSoup
from cookielib import CookieJar
import serial
import threading
import datetime
import shutil
from pynmea import nmea

ser = 0
lat = 0
long = 0
pos_x = 0
pos_y = 0
alt = 0
i = 0 #x units for altitude measurment
BAUDRATE = 4800
#adjust these values based on your location and map, lat and long are in decimal degrees
TRX = -105.1621          #top right longitude
TRY = 40.0868            #top right latitude
BLX = -105.2898          #bottom left longitude
BLY = 40.001             #bottom left latitude
BAUDRATE = 4800
lat_input = 0            #latitude of home marker
long_input = 0           #longitude of home marker

token = ["00000000","xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"]

threadStop = 0
gpsLine = ""

def init_serial():    
    comnum = 'COM3'  
    # configure the serial connections 
    global ser, BAUDRATE
    ser = serial.Serial()
    ser.baudrate = BAUDRATE
    ser.port = comnum
    ser.timeout = 1
    ser.open()
    ser.isOpen()
    #thread()
    
def scan():
    #scan for available ports. return a list of tuples (num, name)
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            available.append( (i, s.name))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available

def save_line():
    global gpsLine
    line = ser.readline()
    line_str = str(line)
    if(line_str[4] == 'G'): # $GPGGA
        if(len(line_str) > 50): 
            gpsLine = line_str

def altitude2():
    global gpsLine
    while (gpsLine=="") or (gpsLine[4]!='G'):
        save_line()
    else:
        if(gpsLine[4] == 'G'): # fifth character in $GPGGA
            if(len(gpsLine) > 50): # when there is a lock, the sentence gets filled with data
                gpgga = nmea.GPGGA()
                gpgga.parse(gpsLine)
                alt = gpgga.antenna_altitude
                print "Altitude: " + alt + "\n"

def ModemLogin():
    targetUrl = "http://192.168.1.1/index.html"
    req = urllib2.Request(targetUrl)
    req.get_method = lambda: 'GET'
    response = urllib2.urlopen(req)    
    UploadResult = response.getcode()

    if UploadResult == 200:
        modemwebpage = response.read()
        sessioncookie = re.search('sessionId=(?:[\d]{1,8})\%2D(?:[\w]{1,31})', modemwebpage)

        if sessioncookie:
            token = sessioncookie.group(0).split('%2D')
            time.sleep(2)
            targetUrl = "http://192.168.1.1/Forms/config"
            postdata = "token=" + token[1] + "&ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password=mullet"
            headers = {"Cookie": token[0] + "-" + token[1]}
            req = urllib2.Request(targetUrl, postdata, headers)
            req.get_method = lambda: 'POST'
            response = urllib2.urlopen(req)
            return response
        else:
            print "[FAIL] No session cookie detected. Unable to login to AC785 Admin Webpage"
            sessioncookie = None
            token = None
            UploadResult = 0
    else:
        print "[FAIL] AC785 Webpage Load Error", UploadResult

    time.sleep(2)

def getSigData(authenticatedPage):
            page = authenticatedPage.read()
            soup = BeautifulSoup(page)            

            #netDiv = soup.findAll(id='network_status_4g')
            #print netDiv[1].contents[1].string
            #print netDiv[1].contents[2].string
            print "4G/LTE data:",
            print "     RSRP: " + soup.select('.m_wwan_signalStrength_rsrp')[0].string,
            print "     RSRQ: " + soup.select('.m_wwan_signalStrength_rsrq')[0].string
            print "(3G data:",
            print "     RSSI: " + soup.select('.m_wwan_signalStrength_rssi')[0].string +")\n"

def main():
    try:
        init_serial()

        for x in range(0,100):
            getSigData(ModemLogin())
            time.sleep(1)
            save_line()
            #altitude2()
    except:
        print "login problem"

if __name__ == "__main__":
    main()
