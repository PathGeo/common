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
oauth=getParameterValue("oauth")

msg={
    "status":"error",
    "msg":"email is not correct! <br>Please check again"
}
results=[]

if(username!='null'):
    trans=transaction.find({"email":username, "oauth": oauth})

    #delete _id key
    for tran in trans:
        tran.pop("_id",None)
        results.append(tran)

    msg=results


print simplejson.dumps(msg)
