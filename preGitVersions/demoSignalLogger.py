import re
import sys
import time
import urllib2
import urllib
import cookielib
from bs4 import BeautifulSoup
from cookielib import CookieJar
import cookielib
import os
import serial
import threading
import datetime
import shutil
from lxml.html import fromstring
from lxml import etree
import requests
#from pynmea import nmea

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

"""def save_line():
    global gpsLine
    line = ser.readline()
    line_str = str(line)
    if(line_str[4] == 'G'): # $GPGGA
        if(len(line_str) > 50): 
            gpsLine = line_str
"""
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

def ModemLogin2():
    targetUrl = "http://192.168.1.1/index.html"
    #cookie stuff
    targetUrl2 = "http://192.168.1.1//Forms/config"

    unAuthResponse = requests.get(targetUrl)    
    sessionCookie = unAuthResponse.cookies
    cookieHeader = { 'Cookie': "sessionId=" + unAuthResponse.cookies['sessionId'] }
    print "\n My Stuff"
    print "\nCookie:"
    print cookieHeader
    print "\nHeaders:\n"
    print unAuthResponse.headers
    
    secToken = sessionCookie['sessionId'].split('-')[1]
    dataPost = "token=" + secToken + "&ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password=admin"
    print "\nPost Data:\n" + dataPost
    response = requests.post(targetUrl2, data= dataPost, headers = cookieHeader)
    #response = requests.post(targetUrl, cookies = sessionCookie, data= dataPost)
    #response = requests.post(targetUrl, data="ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password=admin")
    
    doc = fromstring(response.text)
    print etree.tostring(doc)
    #print doc.find("head/script").text

    
    """
    unAuthResponse = requests.get(targetUrl)
    #print unAuthResponse.text
    sessionCookie = unAuthResponse.cookies
    response2 = requests.get(targetUrl, cookies = sessionCookie)
    print unAuthResponse.cookies
    print response2.cookies
    """
    


    """    
    cookiej = CookieJar()
    targetUrl = "http://192.168.1.1/index.html"
    req = urllib2.Request(targetUrl) 
    response = urllib2.urlopen(req)
    cookiej.extract_cookies(response,req)
    response2 = urllib2.urlopen(req)
    """
def Login():
    targetUrl = "http://192.168.1.1/index.html"

    unAuthResponseMe = requests.get(targetUrl)

    req = urllib2.Request(targetUrl)
    req.get_method = lambda: 'GET'
    unAuthResponseThem = urllib2.urlopen(req)

    #print unAuthResponseMe.text
    print "##########################################################"
    #print unAuthResponseThem.read()

    print unAuthResponseMe.headers
    print "##########################################################"
    print unAuthResponseThem.headers

    
    
def ModemLogin():
    #print "debugaa"    

    targetUrl = "http://192.168.1.1/index.html"
    #print "debugbb"    
    req = urllib2.Request(targetUrl)
    #print "debugccb"
    req.get_method = lambda: 'GET'
    #print "debugcc"
    response = urllib2.urlopen(req)
    #print "debugdd"
    UploadResult = response.getcode()
    #print "debugee"

    if UploadResult == 200:
        #print "debugff"
        modemwebpage = response.read()
        #print "debuggg"
        sessioncookie = re.search('sessionId=(?:[\d]{1,8})\%2D(?:[\w]{1,31})', modemwebpage)

        if sessioncookie:
            #print "debug1"    
            token = sessioncookie.group(0).split('%2D')
            #time.sleep(2)
            targetUrl2 = "http://192.168.1.1/Forms/config"
            postdata = "token=" + token[1] + "&ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password=admin"
            #print "\n His Stuff"
            headers = {"Cookie": token[0] + "-" + token[1]}
            #print headers
            req = urllib2.Request(targetUrl2, postdata, headers)
            req.get_method = lambda: 'POST'
            response = urllib2.urlopen(req)
            print response
            
            #print "debug2"
            response2 = requests.post(targetUrl, data= postdata, headers = headers)
            print response2
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
            #print "debug3"
            page = authenticatedPage.read()
            #print "debug4"
            #print page

            doc = fromstring(page)
            print "4G/LTE data:",
            print "     RSRP: " + doc.find_class('m_wwan_signalStrength_rsrp')[0].text

            #el = doc.find_class('m_wwan_signalStrength_rsrp')[0]
            #print el.text
            
            
            """
            soup = BeautifulSoup(page)

            print "debug5"
            #netDiv = soup.findAll(id='network_status_4g')
            #print netDiv[1].contents[1].string
            #print netDiv[1].contents[2].string
            print "4G/LTE data:",
            print "     RSRP: " + soup.select('.m_wwan_signalStrength_rsrp')[0].string,
            print "     RSRQ: " + soup.select('.m_wwan_signalStrength_rsrq')[0].string
            print "(3G data:",
            print "     RSSI: " + soup.select('.m_wwan_signalStrength_rssi')[0].string +")\n"
            """
def Login3():
    targetUrl = "http://192.168.1.1/index.html"
    targetUrl2 = "http://192.168.1.1/Forms/config"
    unAuthResponse = requests.get(targetUrl)
    sessionCookie = unAuthResponse.cookies
    secToken = sessionCookie['sessionId'].split('-')[1]
    dataPost = "token=" + secToken + "&ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password=admin"
    response2 = requests.post(targetUrl2, cookies = sessionCookie, data = dataPost)
    return response2

def main():
    try:
        #init_serial()
        #Login()
        Login3()
        #ModemLogin()
        """
        for x in range(0,100):
            getSigData(ModemLogin())
            #time.sleep(1)
            #save_line()
            #altitude2()
            """
    except:
        print "login problem: ", sys.exc_info()[0]

if __name__ == "__main__":
    main()
