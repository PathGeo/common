from pymongo import MongoClient
from datetime import datetime
import time, json
from os import path


client=MongoClient()	

#save data as excel--------------------------------------------------------
def saveDataAsExcel(data, outputFileName):
	import xlwt

	book = xlwt.Workbook(encoding="UTF-8")
	sheet = book.add_sheet('Data')
	
	columns = data[0].keys()
	
	for colIndx, column in enumerate(columns):
		sheet.write(0, colIndx, column)
		

	for rowIndx, row in enumerate(data):
		for colIndx, column in enumerate(columns):
			val = row.get(column, '')
			sheet.write(rowIndx+1, colIndx, val)
	
	curDir = path.dirname(path.realpath(__file__))	
	book.save(curDir + "\\" + outputFileName)
#--------------------------------------------------------------------------

pathgeoTrans=client["pathgeo"]["transaction"]
pathgeoUser=client["pathgeo"]["user"]

startTime=time.mktime(datetime.strptime("2013-08-23 00:00:00 ", "%Y-%m-%d %H:%M:%S ").timetuple())

results=[]
for user in pathgeoUser.find():
    date=user["dateRegister"].split(" ")[0]
    date=datetime.strptime(date, "%Y-%m-%d")
    timestamp=time.mktime(date.timetuple())

    if(timestamp>=startTime):
        results.append({
            "email": user["email"],
            "dateRegister": user["dateRegister"],
            "leftCredit": user["credit"],
            "accountType": user["accountType"]
        })

if(len(results)>0):
    filepath="..\\report\\pathgeoUserReport.xls"
    saveDataAsExcel(results, filepath)
    print "Location: "+ filepath +"\n"



