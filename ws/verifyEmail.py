
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
    user=collection.find_one({"email": email})

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


if(email is not None and code is not None):
    msg=checkEmailHashCode(email, code)


if msg["status"]=="ok":
    print "Location: https://www.pathgeo.com \n"
else:
    print "Content-Type: text/html \n"
    print simplejson.dumps(msg)
