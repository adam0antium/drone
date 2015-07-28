from lxml.html import fromstring
import requests
  
def GetSigData(loggedInCookie):
    targetUrl = "http://192.168.1.1/index.html"    
    homePage = requests.get(targetUrl, cookies = loggedInCookie)
    doc = fromstring(homePage.text)
    
    print "4G/LTE data:",
    print "     RSRP: " + doc.find_class('m_wwan_signalStrength_rsrp')[0].text, 
    print "     RSRQ: " + doc.find_class('m_wwan_signalStrength_rsrq')[0].text
            
def Login():
    targetUrl = "http://192.168.1.1/index.html"
    configFormUrl = "http://192.168.1.1/Forms/config"
    unAuthResponse = requests.get(targetUrl)
    sessionCookie = unAuthResponse.cookies
    secToken = sessionCookie['sessionId'].split('-')[1]
    postData = "token=" + secToken + "&ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password=admin"
    requests.post(configFormUrl, cookies = sessionCookie, data = postData)
    return sessionCookie

def main():
    try:        
        for x in range(0,100):
            GetSigData(Login())
 
    except:
        print "login problem: ", sys.exc_info()[0]

if __name__ == "__main__":
    main()
