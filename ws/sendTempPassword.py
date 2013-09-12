#Standard Libraries
import cgi #import cgi library to get url parameters from users
import json  #import libaray to use json
import re
from pymongo import MongoClient
from hashlib import sha512
from uuid import uuid4
import requests

SEND_EMAIL_URL = 'http://ec2-54-235-14-134.compute-1.amazonaws.com/python/sendMail.py?contentType=forgetPW&email=%s&code=%s'
VALID_CHARS = '@!*$0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'


def generateTempPassword():
	from random import choice, randint

	#length of temp password is between 7 and 12 characters
	length = randint(7, 12)
	return ''.join(choice(VALID_CHARS) for _ in range(length))
	
	
form = cgi.FieldStorage()
email = None if 'email' not in form else form['email'].value

col = MongoClient().pathgeo.user

if not email:
	print ''
	print json.dumps({'status': 'error', 'message': 'No email parameter passed.'})
	exit(1)

	
tempPassword = generateTempPassword()

#store the hashed value of the new password, along with the new salt
user = col.find_one({'email': re.compile(email, re.IGNORECASE)})

if not user:
	print ''
	print json.dumps({'status': 'error', 'message': 'Email could not be found! Please sign up first.'})
	exit(1)

userUUID = uuid4().hex
user["userUUID"] = userUUID
user["password"] = sha512(tempPassword + userUUID).hexdigest()
col.save(user)

url = SEND_EMAIL_URL % (email, tempPassword)
		
resp = requests.get(url)
	
if not resp.ok:
	print ''
	print json.dumps({'status': 'error', 'message': 'Error occurred when sending temporary password to EC2.'})
else:
	print ''
	print json.dumps({'status': 'ok', 'message': 'looks good!'})