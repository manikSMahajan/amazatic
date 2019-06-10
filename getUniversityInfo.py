from selenium import webdriver
from urllib.parse import urlparse
import bs4
import json
import sys
import requests
import mysql.connector

links = {}

def getRank(obj):
	rank = obj.find("td")
	spclass = rank.get("class")
	if "rank" in spclass:
		sp = rank.find("span", attrs= {"class":"rank"})
		return sp.text.replace("=","")

def getUniName(obj):

	name  = obj.find("a", attrs= {"class":"title"})
	if name is not None:
		hyperLink = name.get("href")
		uniName  = name.find('b').text
		links.update({uniName: hyperLink})
		return uniName

def getCityName(obj):
	cityName  = obj.find("td", attrs= {"class":"city"})
	if cityName is not None:
		return cityName.find("div").text

def getCountry(obj):
	country = obj.find("td", attrs = {"class" : " country"})
	if country is not None:
		return country.find("div").text

def getStartDate(obj):
	s = obj.find("div", attrs= {"class": "data-boxes program-start-dates"})
	if s is not None:
			return s.find("div", attrs = {"class":"data"}).text

def getClassSize(obj):
	s = obj.find("div", attrs= {"class": "data-boxes class-size"})
	if s is not None:
			return s.find("div", attrs = {"class":"data"}).text

def getAvgWorkExp(obj):
	s = obj.find("div", attrs= {"class": "data-boxes avg-work-experience"})
	if s is not None:
			return s.find("div", attrs = {"class":"data"}).text

def getAvgStdAge(obj):
	s = obj.find("div", attrs= {"class": "data-boxes program-average-age"})
	if s is not None:
			return s.find("div", attrs = {"class":"data"}).text
	
def getintStd(obj):
	s = obj.find("div", attrs= {"class": "data-boxes international-students"})
	if s is not None:
			return s.find("div", attrs = {"class":"data"}).text
def getWomenStd(obj):
	s = obj.find("div", attrs= {"class": "data-boxes program-female-students"})
	if s is not None:
			return s.find("div", attrs = {"class":"data"}).text
def getAvgSal(obj):
	s = obj.find("div", attrs= {"class": "data-boxes avg-salary-grad"})
	if s is not None:
			return s.find("div", attrs = {"class":"data"}).text
def getScholarship(obj):
	s = obj.find("div", attrs= {"class": "data-boxes school-sponsore"})
	if s is not None:
			return s.find("div", attrs = {"class":"data"}).text
def getAccreditations(obj):
	s = obj.find("div", attrs= {"class": "data-boxes program-accreditations"})
	if s is not None:
			return s.find("div", attrs = {"class":"data"}).text
def baseConnection(mysqlUser,mysqlPassword,dbname,host):
	mydb = mysql.connector.connect(
	  host=host,
	  user=mysqlUser,
	  passwd=mysqlPassword
	)
	mycursor = mydb.cursor()
	mycursor.execute("CREATE DATABASE IF NOT EXISTS %s" %(dbname))

	mydb = mydb = mysql.connector.connect(
	  host=host,
	  user=mysqlUser,
	  passwd=mysqlPassword,
	  database=dbname
	)
	mycursor = mydb.cursor()
	mycursor.execute("CREATE table IF NOT EXISTS UniversityDetails(name varchar(40) NOT NULL PRIMARY KEY , rank int, city varchar(60) , country varchar(20));")
	mycursor.execute("delete from UniversityDetails")
	mycursor.execute("CREATE table IF NOT EXISTS Highlights(UniName varchar(40) , startDate varchar(40), classSize varchar(10), avgWorkExp varchar(10) , avgStudentAge varchar(10)	, intStudent varchar(20), womenStudent varchar(20), avgSal varchar(30), Scholarship varchar(6), Accreditations varchar(40));")
	return mydb , mycursor
def main(URL , mysqlUser , mysqlPassword , databaseName, host):
	uniDetails = {"data" : []}

	url =URL
	items = urlparse(url)
	urlWithoutEndPoint = items.scheme + "://" + items.netloc
	browser = webdriver.Chrome()
	browser.get(url)
	beautiObj = bs4.BeautifulSoup(browser.page_source, "html.parser")
	for div in  beautiObj.find_all(attrs={'id':"qs-rankings"}):
		tbody = div.find("tbody")
		for tr in tbody.find_all("tr"):
			uniDetails["data"].append({"Rank": getRank(tr), "Name": getUniName(tr), "City": getCityName(tr), "Country": getCountry(tr)})

	# print(links)
	for key , value in links.items():
		highlightData = requests.get(urlWithoutEndPoint+value)
		soup = bs4.BeautifulSoup(highlightData.text, "html.parser")
		for index, element in enumerate(uniDetails["data"]):
			for key1 , value1 in list(element.items()):
				if key1 == "Name":
					if value1 == key:
						d = {"highLights": { "Start Month" : getStartDate(soup),
							  "Class Size" : getClassSize(soup),
							  "Avg Work Exp": getAvgWorkExp(soup),
							  "Avg. Student Age" : getAvgStdAge(soup),
							  "international-students" : getintStd(soup),
							  "women std": getWomenStd(soup),
							  "Avg. salary" : getAvgSal(soup),
							  "Scholarship" : getScholarship(soup),
							  "Accreditations": getAccreditations(soup)	}}

						uniDetails["data"][index].update(d)
	mydb ,cursor = baseConnection(mysqlUser, mysqlPassword, databaseName,host)
	UniQry = "insert into UniversityDetails(name , rank , city , country) values (%s, %s , %s , %s);"
	highLightsQry = "insert into Highlights(UniName  , startDate , classSize , avgWorkExp  , avgStudentAge, intStudent , womenStudent , avgSal, Scholarship, Accreditations) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
	for element in uniDetails["data"]:
		
		name = element["Name"]
		rank = element["Rank"]
		city = element["City"]
		country = element["Country"]
		startDate = element["highLights"]["Start Month"]
		classSize = element["highLights"]["Class Size"]
		avgWorkExp = element["highLights"]["Avg Work Exp"]
		avgStudentAge = element["highLights"]["Avg. Student Age"]
		international_students = element["highLights"]["international-students"]
		womenStudent = element["highLights"]["women std"]
		avgSal = element["highLights"]["Avg. salary"]
		Scholarship = element["highLights"]["Scholarship"]
		Accreditations = element["highLights"]["Accreditations"]
		cursor.execute(UniQry,(name,rank, city, country))
		cursor.execute(highLightsQry, (name, startDate, classSize, avgWorkExp, avgStudentAge, international_students, womenStudent , avgSal, Scholarship , Accreditations))

	mydb.commit()
	with open("output.json", "w") as fp:
		json.dump(uniDetails, fp, indent =4)
if __name__ == '__main__':
	try:
		if len(sys.argv) == 2:
		    data = json.load(open(sys.argv[1]))
		    main(data["url"], data["mysqlUser"] , data["mysqlPassword"], data["dbName"], data["host"])
		    print("University Details are  stored in 'UniversityDetails' and 'Highlights' table of MySQL.")
		else:
		    print("insufficeint arguments, Taking default config.")
		    data = json.load(open("./config.json"))
		    main(data["url"], data["mysqlUser"] , data["mysqlPassword"], data["dbName"], data["host"])
		    print("University Details are  stored in 'UniversityDetails' and 'Highlights' table of MySQL.")
	except (mysql.connector.Error) as e:
	    print(e)
	except FileNotFoundError as error:
		print(error)
	except (ConnectionError, Exception,KeyError) as error:
		print(error)
