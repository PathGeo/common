#Standard Libraries
import cgi #import cgi library to get url parameters from users
import json as simplejson  #import libaray to use json
import requests
import datetime

#Mongo
from pymongo import MongoClient


print "Content-Type: text/html; charset=utf-8 \n"
print """
<head>
    <style type='text/css'>
        html, body {width:100%; height:100%; font-family:Arial; margin:0px; padding:0px; overflow:hidden; }
        div {width:100%; height:100%; margin:0 auto; overflow:hidden; text-align:center; background-color:#f1f1f1 }
        h2 {background-color:#cccccc; color:#ffffff; padding:20px; margin-top:0px; }
        h2 p {color:#777777; font-size:16px; }
        ul {list-style:none; padding:0px; margin:0px; width:100%; }
        ul li {float:left;  width:33%;  }
        ul li img {width:50%;}
    </style>
</head>
</body>
<div>
    <h2>Authorizing....<p>PathGeo is syncing account information with your Google account. <br>Please wait.</p></h2><p></p>
    <ul>
        <li><img src='../images/PathGeo-circle-color.png'/></li>
        <li><img src='../images/loading2.gif' style='margin-top:50px; '/></li>
        <li><img src='../images/1376249138_social_google_box.png'/></li>
    </ul>
</div>
</body>
"""

app={
    "parameter":cgi.FieldStorage()
}



#get value from URL parameter--------------------------------------------
def getParameterValue(name):
    value=None
    
    if(name in app["parameter"] and app["parameter"][name].value!=""):
        value=app["parameter"].getvalue(name)

    return value
#--------------------------------------------------------------------------


#get token from Google-----------------------------------------------------
def getToken(code):
    url="https://accounts.google.com/o/oauth2/token"
    header={"content-type":"application/x-www-form-urlencoded"}
    data={
        "code": code,
        "redirect_uri":"https://www.pathgeo.com/common/ws/oauth_google.py",
        #"redirect_uri":"http://localhost/github/common/ws/oauth_google.py",
        "client_id":"604420150698.apps.googleusercontent.com",
        "client_secret":"ywNxUIQwWkG96naXwHZkUbwv",
        "grant_type":"authorization_code"
    }
  
    r=requests.post(url, headers=header, data=data, verify=False)

    #if request is successful
    if(r.status_code==200):
        return simplejson.loads(r.text)
    else:
        return None
#--------------------------------------------------------------------------


#get user Info-------------------------------------------------------------
def getUserInfo(token):
    url="https://www.googleapis.com/oauth2/v1/userinfo"
    header={"content-type":"application/json"}
    data={
        "access_token":token
    }
    
    r=requests.get(url, headers=header, params=data)
    r.encoding='utf-8'
    
    #if request is successful
    if(r.status_code==200):
        return simplejson.loads(r.text)
    else:
        print 'getUserInfo error: '+ r.text
        return None
#--------------------------------------------------------------------------


#save email in Mongo to detemine if the email is going to signup or login
def saveinMongo(email):
    from hashlib import sha512
    from uuid import uuid4

    
    userCollection=MongoClient()["pathgeo"]["user"]
    user=userCollection.find_one({"email":email, "oauth":"google"})
    infos=["email", "dateRegister", "accountType", "credit", "oauth"]
    accountInfo={}
    status="login"

    #if the user does not exist >> sign up, else >> login
    if(user is None):
        user={
            "email":email,
            "password":None,
            "emailSent":False,
            "emailVerified": False,
            "dateRegister": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"),
            "accountType": "free",
            "credit": 1500,
            "oauth":"google",
            "userUUID": uuid4().hex,
            "emailSent": False,
            "emailSentMsg": None,
            "emailVerified": True
        }
        status="signup"
        userCollection.save(user)
    
    #return account info
    for info in infos:
        accountInfo[info]=user[info]
    return accountInfo, status
#------------------------------------------------------------------------------



#main
code=getParameterValue('code')
error=getParameterValue('error')

msg={
    "status":"error",
    "msg":""
}

if(error is not None):
    msg["msg"]=error
else:
    if(code is not None):
        #send a request to get valid token
        result=getToken(code)
        if(result is not None):
            token=result["access_token"]
            expire=result["expires_in"]

            #get User info by the requested Token
            userInfo=getUserInfo(token)

            #if getUserInfo sucesseed
            if userInfo is not None:
                accountInfo, status=saveinMongo(userInfo["email"])

                msg=None
                '''
                msg={
                    "status":"ok",
                    "msg":"signup/login succesfully",
                    "account": accountInfo
                }
                '''
                #send accountInfo back to the main webpage ('the parent of iframe') function: oauth_callback
                print "<script>window.opener.oauth_callback("+ simplejson.dumps(accountInfo)+", '" + status + "');</script>"
            else:
                msg["msg"]="Error: userInfo: \n" + userInfo
        else:
            msg["msg"]="code is not correct!"
    else:
        msg["msg"]="no code in the URL parameter"



if(msg is not None):
    print simplejson.dumps(msg)
    
