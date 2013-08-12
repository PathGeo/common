
#Standard Libraries
import cgi #import cgi library to get url parameters from users
import json as simplejson  #import libaray to use json
from pymongo import MongoClient

print "Content-Type: text/html \n"


app={
    "parameter":cgi.FieldStorage()
}




#queyr db to get the account info-------------------------------------------------------------------
def getAccountInfo(email, oauth):
    msg={
        "status":"ok",
        "msg": "query succesfully",
        "account":{}
    }


    collection=MongoClient()["pathgeo"]["user"]
    user=collection.find_one({"email": email, "oauth":oauth})

    #check if email exists
    if(user is not None):
        accountInfo={}
        infos=["email", "dateRegister", "accountType", "credit"]

        for info in infos:
            accountInfo[info]=user[info]
        
        msg["account"]=accountInfo
        return msg
    else:
        return {
            "status":"error",
            "msg": "No such account. Please check again."
        }    
#---------------------------------------------------------------------------------------


#get value from URL parameter--------------------------------------------
def getParameterValue(name):
    value="null"
    
    if(name in app["parameter"] and app["parameter"][name].value!=""):
        value=app["parameter"].getvalue(name)

    return value
#--------------------------------------------------------------------------



#main
email=getParameterValue("email")
oauth=getParameterValue("oauth")

msg={
    "status":"error",
    "msg":"email is missing! Please check again"
}


if(email!='null'):
    #get account info
    msg=getAccountInfo(email, oauth)

print simplejson.dumps(msg)
