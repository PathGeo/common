
#Standard Libraries
import cgi #import cgi library to get url parameters from users
import json as simplejson  #import libaray to use json
from pymongo import MongoClient
from hashlib import sha512
from uuid import uuid4


app={
    "parameter":cgi.FieldStorage(),
    "dbName":"pathgeo",
    "dbCollection": "user"
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

    
#verify email and hashcode--------------------------------------------
def checkEmailHashCode(email, code):
    #get userUUID from MongoDB
    collection=MongoClient()["pathgeo"]["user"]
    user=collection.find_one({"email": email, "oauth":None})

    result={
        "status":"error",
        "msg":"No existing account: "+ email
    }
    
    if(user is not None):
        if("emailVerified" in user and user["emailVerified"]):
            result={
                "status":"ok",
                "msg":"email verified"
            }
        else:
            if("userUUID" in user and user["userUUID"] is not None):
                userUUID=user["userUUID"]
                hashcode = sha512("emailVerify@PathGeo" + userUUID).hexdigest()
                
                if(hashcode==code):
                    user["emailVerified"]=True
                    collection.save(user)
                    
                    result={
                        "status":"ok",
                        "msg":"email verified"
                    }
                else:
                    result["msg"]="hashcode is not correct!"
            else:
                result["msg"]="no userUUID property in the user collection"
    
    return result
#--------------------------------------------------------------------------
            

#main
email=getParameterValue("email")
code=getParameterValue("code")

msg={
    "status":"error",
    "msg":"email or code is not correct! Please check again"
}


print "Content-Type: text/html \n"


if(email is not None and code is not None):
    msg=checkEmailHashCode(email, code)




if msg["status"]=="ok":
    print """
        <html><head>
            <style>
                html, body {width:100%; height:100%; overflow:hidden; padding:0px; margin:0px; font-family:Arial;}
                #mainContent {width:70%; height:30%; margin:0 auto; border:0px; margin-top:100px;  }
                #mainContent img {float:left; width:100px; height:100px; margin-top:20px; }
                #mainContent div {float:right;}
            </style>
        </head>

        <body>
            <div id='mainContent'>
                <img src='../images/PathGeo-circle-color.png'>

                <div>
                    <h2>Your Email has been verified.</h2>
                    The webpage will be automatically redirecting to PathGeo homepage in <label id='countdown'>10</label> seconds. <p></p>
                    Or you can click <a href='https://www.pathgeo.com'>here</a> to skip waiting. 
                </div>
            </div>

            <script type='text/javascript'>
                var countdown=document.getElementById("countdown");
                var number=9;
                var countdownInterval=setInterval(function(){
                
                    if(number>0){
                        countdown.innerHTML=number
                    }else{
                        clearInterval(countdownInterval)
                        window.location.href="https://www.pathgeo.com";
                    }

                    number--;
                }, 1000)
            </script>
        </body></html>
        
    """
else:
    print simplejson.dumps(msg)
