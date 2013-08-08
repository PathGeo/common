import cgi, json as simplejson
from pymongo import MongoClient

print "Content-Type: text/html \n"


#global variable
client=MongoClient()
transaction=client["pathgeo"]["transaction"]
urlParameter=cgi.FieldStorage()


#get value from URL parameter--------------------------------------------
def getParameterValue(name):
    value="null"
    
    if(name in urlParameter and urlParameter[name].value!=""):
        value=urlParameter.getvalue(name)

    return value
#--------------------------------------------------------------------------



#main
username=getParameterValue("username")
msg={
    "status":"error",
    "msg":"email is not correct! <br>Please check again"
}


if(username!='null'):
    result=list(transaction.find({"email":username}))
    msg=result



print simplejson.dumps(msg)
