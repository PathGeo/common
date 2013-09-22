import hmac, hashlib, cgi, json as simplejson, datetime
from pymongo import MongoClient

print "Content-Type: text/html \n"

#global variable
client=MongoClient()
transaction=client["pathgeo"]["transaction"]
userCollection=client["pathgeo"]["user"]
urlParameter=cgi.FieldStorage()


#get value from URL parameter--------------------------------------------
def getParameterValue(name):
    value=None
    
    if(name in urlParameter and urlParameter[name].value!=""):
        value=urlParameter.getvalue(name)

    if(value is not None and value.upper()=='NULL'):
        value=None
        
    return value
#--------------------------------------------------------------------------



username=getParameterValue("email")
oauth=getParameterValue("oauth")
plan=getParameterValue("plan")
card_name=getParameterValue("card_name")
card_number=getParameterValue("card_number")
card_authNumber=getParameterValue("card_authNumber")
card_expiryDate=getParameterValue("card_expiryDate")




#calculate hascode------------------------------------------------------------
def calculateHashcode(x_login, x_fp_sequence, x_fp_timestamp, x_amount, x_currency):
    # Instantiate hmac with Transaction key (HMAC-MD5)
    digest_maker = hmac.new('TEKIi3lkko_WjRfE_uJ0', '', hashlib.md5)

    # Instantiate hmac with Transaction key (HMAC-SHA1)
    # digest_maker = hmac.new('TEKIi3lkko_WjRfE_uJ0', '', hashlib.sha1)

    format = '%(x_login)s^%(x_fp_sequence)s^%(x_fp_timestamp)s^%(x_amount)s^%(x_currency)s'
    data =  format % {'x_login' : x_login,
                      'x_fp_sequence' : x_fp_sequence, 
                      'x_fp_timestamp' : x_fp_timestamp, 
                      'x_amount' : x_amount, 
                      'x_currency' : x_currency}

    digest_maker.update(data)
    x_fp_hash = digest_maker.hexdigest()

    return x_fp_hash
#--------------------------------------------------------------------------


#add credit and record transaction
def addCredit(credit, accountType):
    user=userCollection.find_one({"email":username, "oauth":oauth})
    credit=int(credit)
    
    if(user is not None):
        if(user["credit"] is not None):
            user["credit"]=user["credit"] + credit
            user["accountType"]=accountType
            userCollection.save(user)

            #account info
            infos=["email", "dateRegister", "accountType", "credit", "oauth"]
            accountInfo={}
            for info in infos:
                accountInfo[info]=user[info]


            #transaction
            transaction.insert({
                "email": username,
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"),
                "description": "[addCredit] " + str(credit),
                "transaction": "None",
                "balance": user["credit"],
                "oauth":oauth
            })
            return "succeed", accountInfo
        else:
            return "no credit field"
    else:
        return "no such user"
#--------------------------------------------------------------------------

#send request to FirstData,our BOA payment service, to pay
def purchase(cardholder_name, cardholder_number, cardholder_authNumber, cardholder_expiryDate, amount):
    import urllib2, base64, requests

    url="https://api.globalgatewayE4.firstdata.com/transaction/v11"
    header={"Content-Type":"application/json", "accept": "application/json"}
    data=simplejson.dumps({
        "gateway_id":"A76868-01",
        "password":"4t72hkjv",
        "transaction_type":"00",
        "amount": str(amount),
        "cardholder_name": str(cardholder_name),
        "cc_number": str(cardholder_number),
        "Authorization_Num": str(cardholder_authNumber),
        "cc_expiry": str(cardholder_expiryDate)
    })
  
    r=requests.post(url, headers=header, data=data, verify=False)

    
    #determine r.text is string(fail) or json(success)
    try:
        json = simplejson.loads(r.text)
    except ValueError, e:
        return {"errorMsg": r.text}
    else:
        return r.json()
    
#--------------------------------------------------------------------------

#record error msg in the transaction log
def recordTransaction(description, amount, result):
    user=userCollection.find_one({"email":username, "oauth":oauth})

    if(user is not None):
        userCredit=user["credit"]

        if(userCredit is not None):
            userCredit=int(userCredit)
            log={
                "email": username,
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"),
                "description": description,
                "transaction": amount,
                "balance": userCredit,
                "oauth":oauth,
                "result": result
            }

            #record log
            transaction.insert(log)

            return "[log error]: log success"
        else:
            return "[log error]: no credit field"
    else:
        return "[log error]: no such user"
#----------------------------------------------------------------------------




#main
msg={
    "status":"error",
    "msg":"email or password is not correct! <br>Please check again"
}


if(username is not None and plan is not None and card_name is not None and card_number is not None and card_authNumber is not None and card_expiryDate is not None):
    #determine amonunt by plan
    plans={
        "plusA":{"price": 5, "credit": 500},
        "plusB":{"price": 10, "credit": 3500},
        "plusC":{"price": 20, "credit": 8000},
        "plusD":{"price": 30, "credit": 12000},
        "pro":{"price": 89, "credit": 40000}
    }
    if(plans[plan] is None):
        msg["msg"]="plan is not correct. Only 'plusA', 'plusB','plusC','plusD' and 'pro' are accepted."
    else:
        amount=int(plans[plan]["price"])
        credit=int(plans[plan]["credit"])
        accountType="plus" if amount < 89 else "pro"

        #connect to the BOA payment service
        outcome=purchase(card_name, card_number, card_authNumber, card_expiryDate, amount)


        #if transaction succeed
        if(outcome.get("errorMsg") is None and outcome["transaction_error"]==0 and outcome["transaction_approved"]==1 and outcome["bank_message"]=="Approved"):
            #add credit
            result, accountInfo=addCredit(credit, accountType)

            if(result!="succeed"):
                msg["msg"]=result
            else:
                msg={
                    "status":"ok",
                    "msg":outcome["ctr"],
                    "accountInfo": accountInfo
                }
        else:
            #transaction failed
            if(outcome.get("errorMsg") is not None):
                msg["msg"]=outcome["errorMsg"]
            else:
                msg["msg"]=outcome["ctr"]
            
        #record log
        r=recordTransaction(msg["msg"], amount, outcome)
        if(r!="[log error]: log success"):
            msg["msg"]=r



print simplejson.dumps(msg)
