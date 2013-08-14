from rauth import OAuth2Service
import urllib2, cgi


app={
    "parameter":cgi.FieldStorage()
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


#base oauth2 services
oauth2service={
    "google":{
        "oauth2Service":OAuth2Service(
            client_id='604420150698.apps.googleusercontent.com',
            client_secret='ywNxUIQwWkG96naXwHZkUbwv',
            name='google',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            base_url='https://accounts.google.com/o/oauth2'
        ),
        "params":{
            "scope":"email",
            "response_type":"code",
            "redirect_uri": "https://www.pathgeo.com/common/ws/oauth_google.py",
            #"redirect_uri": "http://localhost/github/common/ws/oauth_google.py",
            "access_type":"online"
        }
    },
    "facebook":{
        "oauth2Service":OAuth2Service(
            client_id='604420150698.apps.googleusercontent.com',
            client_secret='ywNxUIQwWkG96naXwHZkUbwv',
            name='google',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            base_url='https://accounts.google.com/o/oauth2'
        ),
        "params":{
            "scope":"email",
            "response_type":"code",
            "redirect_uri": "http://localhost/python/oauth_facebook.py",
            "access_type":"online"
        }
    }
}


provider=getParameterValue("provider")


if provider in oauth2service:
    service=oauth2service[provider]["oauth2Service"]
    params=oauth2service[provider]["params"]

    url=service.get_authorize_url(**params)

    #redirect to google authorize url
    print "Location: "+ url +"\n"

else:
    print "Content-Type: text/html; charset=utf-8 \n"
    print "No type parameter. Please check again"

