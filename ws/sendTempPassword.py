#Standard Libraries
import cgi #import cgi library to get url parameters from users
import json  #import libaray to use json
import requests

NEW_PASSWORD_URL = 'http://ec2-54-235-14-134.compute-1.amazonaws.com/python/sendMail.py?contentType=forgetPW&email=%s&code=%s'
VALID_CHARS = '@!*$0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'


def generateTempPassword():
	from random import choice, randint

	#length of temp password is between 7 and 12 characters
	length = randint(7, 12)
	return ''.join(choice(VALID_CHARS) for _ in range(length))
	
	
form = cgi.FieldStorage()
email = None if 'email' not in form else form['email'].value

if not email:
	print ''
	print json.dumps({'error': 'No email parameter passed.'})
	exit(1)

	
tempPassword = generateTempPassword()
url = NEW_PASSWORD_URL % (email, tempPassword)
	
resp = requests.get(url)
	
if not resp.ok:
	print ''
	print json.dumps({'error': 'Error occurred when sending temporary password to EC2.'})
else:
	print ''
	print json.dumps({'ok': 'looks good!'})