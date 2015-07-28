from lxml.html import fromstring
import requests
import sys
import os


  
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
    secToken = sessionCookie['sessionId'].split('-')[1]
    postData = "token=" + secToken + "&ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password=admin"
    requests.post(configFormUrl, cookies = sessionCookie, data = postData)
    return sessionCookie

def OpenLogFile():
    lognumber = 0    
    logfileName = 'logfile0.log'
    while os.path.isfile(logfileName):
        lognumber += 1
        logfileName = '/home/pi/Desktop/droneLogFiles/logfile' + str(lognumber) + '.log'
    logFile = open(logfileName , 'w')
    return logFile

def main():
    try:
        sessionCookie = Login()
#        logFile = OpenLogFile()
        for x in range(0,100):
#            logFile.write(GetSigData(sessionCookie))
             print GetSigData(sessionCookie)
    except:
        print "login problem: ", sys.exc_info()[0]

if __name__ == "__main__":
    main()
