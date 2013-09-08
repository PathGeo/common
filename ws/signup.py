
#Standard Libraries
import cgi #import cgi library to get url parameters from users
import json as simplejson  #import libaray to use json
from pymongo import MongoClient
import smtplib #send email by using smtp
import datetime
import requests


print "Content-Type: text/html \n"


app={
    "parameter":cgi.FieldStorage(),
    "dbName":"pathgeo",
    "dbCollection": "user",
    "smtpServer":"smtp.gmail.com",
    "smtpPort":587,
    "gmailAccount":"pathgeo@gmail.com",
    "gmailPassword": "NETRE_2012"
}



#get value from URL parameter--------------------------------------------
def getParameterValue(name):
    value=None
    
    if(name in app["parameter"] and app["parameter"][name].value!=""):
        value=app["parameter"].getvalue(name)

    if(value is not None and value.upper()=='NULL'):
        value=None
        
    return value
#--------------------------------------------------------------------------

    
#register user to db-------------------------------------------------------
def register(obj):
    from hashlib import sha512
    from uuid import uuid4
    
    client=MongoClient()
    collection=client[app["dbName"]][app["dbCollection"]]
    user=collection.find_one({"email":obj["email"]})
    
    #determine whether email is already registered
    if (user is not None):
        return {
            "status":"error",
            "msg":"The email address is already existed. Please use other email to sign up"
        }
    else:
        #generate userUUID and emailHashcode
        userUUID = uuid4().hex
        emailHashcode = sha512("emailVerify@PathGeo" + userUUID).hexdigest()

        #send email
        emailSent, emailSentMsg=sendEmail(email, emailHashcode)

        obj["userUUID"]=userUUID
        obj["emailSent"]=emailSent
        obj["emailSentMsg"]=emailSentMsg
        obj["emailVerified"]=False
        obj["password"]=sha512(obj["password"] + userUUID).hexdigest()
        
        collection.insert(obj)


        #define which field need to be sent back to client
        infos=["email", "dateRegister", "accountType", "credit", "oauth"]
        accountInfo={}
        for info in infos:
            accountInfo[info]=obj[info]

        return {
            "status":"ok",
            "msg":"signup succesfully",
            "account":accountInfo
        }
#----------------------------------------------------------------------------


#send email for validation-------------------------------------------------
def sendEmail(email, hashcode):
    #due to the smtp port is locked in the SDSU, we pass the request to EC2 server to send email
    url="http://ec2-54-235-14-134.compute-1.amazonaws.com/python/sendMail.py"
    header={"content-type":"application/x-www-form-urlencoded"}
    data={
        "email": email,
        "contentType":"verify",
        "code": hashcode
    }
    result=requests.post(url, headers=header, data=data, verify=False)

    emailSent=False
    msg=simplejson.loads(result.text)
    if(result.status_code==200 and msg is not None and "status" in msg and msg["status"]=="ok"):
        emailSent=True

    return emailSent, result.text
    
    '''
    subject="[Pathgeo] Confirm your email address"
    body="""
    Dear Customers: <p></p> We are excited to have you with Pathgeo. <br>
    Please confirm your email by clicking the following link. <p></p>
    <a href='https://www.pathgeo.com/demo/maptime/python/verify.py?id=""" + id + """ target='_blank'>https://www.pathgeo.com/demo/maptime/python/verify.py?id=""" + id + """</a><p></p> 
    This link will redirect you to our Pathgeo product: MapTime.<br>
    From there you can start to upload your customers' data and geotagging on the map!<br>
    If you have any comments or feedbacks, please feel free to <a href='mailto:pathgeo@mail.com'>contact us</a><p></p>
    Sincerely,<br>Pathgeo"""

    body = "" + body + ""

    headers = [
        "From: " + app["gmailAccount"],
        "Subject: " + subject,
        "To: " + email,
        "MIME-Version: 1.0",
        "Content-Type: text/html"
    ]
    headers = "\r\n".join(headers)

    session = smtplib.SMTP(app["smtpServer"], app["smtpPort"])
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(app["gmailAccount"], app["gmailPassword"])

    session.sendmail(app["gmailAccount"], email, headers + "\r\n\r\n" + body)
    session.quit()
    '''
    
#------------------------------------------------------------------



#main
email=getParameterValue("email")
password=getParameterValue("password")


msg={
    "status":"error",
    "msg":"email or password is not correct! Please check again"
}

if(email is not None and password is not None):
    #sign up
    #user obj
    obj={
        "email":email,
        "password":password,
        "dateRegister": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "accountType": "free",
        "credit": 6000,
        "oauth":None
    }

    #resiter a user account and print result
    msg=register(obj)
   

print simplejson.dumps(msg)
