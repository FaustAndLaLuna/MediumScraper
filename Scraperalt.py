import urllib.request
import requests
import bs4
import pandas as pd
import time
import datetime
import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver


"""
@author: Faust and la luna
Self: tagString

De un tag, hace un crawl de la pagina medium.
Luego lo manda a ser analizado.
"""

def request(self, date):
	StartURL = "https://medium.com/tag/" + self + "/archive/" + date.strftime("%Y/%m/%d")
	print(StartURL)
	option = webdriver.ChromeOptions()
	chrome_prefs = {}
	option.experimental_options["prefs"] = chrome_prefs
	chrome_prefs["profile.default_content_settings"] = {"images":2}
	chrome_prefs["profile.managed_default_content_settings"] = {"images":2}
	driver = webdriver.Chrome(options=option)
	driver.get(StartURL)
	time.sleep(0.1)
	if(driver.current_url != StartURL):
		print("Cambiando de fecha, no hay articulos en: " + date.strftime("%Y - %m - %d"))
		driver.quit()
		return
	##SCROLLING TO LOAD ALL DATA
	SCROLL_PAUSE_TIME = 0.1
	last_height = driver.execute_script("return document.body.scrollHeight")
	while True:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(SCROLL_PAUSE_TIME)
		new_height = driver.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
			break
		last_height = new_height

	response = driver.execute_script("return document.documentElement.outerHTML")
	soup = BeautifulSoup(response, 'lxml')
	articles = []

	for link in soup.find_all(class_="postArticle postArticle--short js-postArticle js-trackPostPresentation js-trackPostScrolls"):
		article = {}
		article["1. Tag"] = self
		article["2. Name"] = link.find(class_=re.compile("author")).a.text
		title = link.find(class_=re.compile("title"))
		if title is None:
			continue
		article["3. Title"] = title.text
		article["4. Date"] = link.time.text
		upvotes = link.find(class_=re.compile("recommend"))
		if upvotes is not None:
			if(upvotes.text == ""):
				article["5. Upvotes"] = '0'
			else:
				article["5. Upvotes"] = upvotes.text
		else:
			article["5. Upvotes"] = "0"
		comments = link.find(class_="button button--chromeless u-baseColor--buttonNormal")
		if comments is not None:
			article["6. Comments"] = comments.text
		else:
			article["6. Comments"] = "0 responses"
		l = link.find(class_="button button--smaller button--chromeless u-baseColor--buttonNormal")
		if l is None:
			continue
		article["7. Link"] = l.get('href')
		articles.append(article)

	for article in articles:
		article["8. Content"] = crawlResponse(article["7. Link"], driver)
	driver.quit()
	parseResponse(articles, self, date)

def crawlResponse(link, driver):
	driver.get(link)
	SCROLL_PAUSE_TIME = 0.1
	last_height = driver.execute_script("return document.body.scrollHeight")
	while True:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(SCROLL_PAUSE_TIME)
		new_height = driver.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
			break
		last_height = new_height
	response = driver.execute_script("return document.documentElement.outerHTML")
	soup = BeautifulSoup(response, 'lxml')
	text = ""
	for paragraph in soup.find_all('p'):
		text += "     " + paragraph.text
	return text

def parseResponse(listOfDicts, tag, date):
	dataFrame = pd.DataFrame(listOfDicts)
	if not os.path.exists(date.strftime('./'+tag+'/Scraped/%Y/%m/')):
		os.makedirs(date.strftime('./'+tag+'/Scraped/%Y/%m/'))
	dataFrame.to_csv(date.strftime('./'+tag+'/Scraped/%Y/%m/%Y-%m-%d-' ) + tag  + ".csv" , encoding="utf-8")
	
def scrapeToToday(tag, date):
	currentDate = datetime.date.today()
	while(date < currentDate):
		request(tag, date)
		date = date + datetime.timedelta(days=1)


if __name__ == "__main__":
	currentDate = datetime.date.today()
	year = input("Dame el año desde el cual comenzar (a partir del 2015)\n")
	year = int(year)
	while (year < 2015 or year > currentDate.year):
		year = input("Dame el año desde el cual comenzar (a partir del 2015)\n")
		year = int(year)
	month = input("Dame el mes (en número de 1 a 12)\n")
	month = int(month)
	while(month > 12) or (month < 1):
		month = input("Dame el mes (en número de 1 a 12)\n")
		month = int(month)
	day = input("Dame el dia (en número de 1 a 31)\n")
	day = int(day)
	while(day > 31) or (day < 1):
		day = input("Dame el dia (en número de 1 a 31)\n")
		day = int(day)
	startDate = datetime.date(year = year, month = month, day = day)
	tag = input("Dame el tag para buscar\n")
	scrapeToToday(tag, startDate)
