# Antonio Maniscalco
# CS 454 Homework 1
# Instructor: Dr. Ben McCamish
# Python Version: 3.8.9
# See README for instructions to run and WriteUp for details on program


import requests
from bs4 import BeautifulSoup
import time
import os
import pandas
import numpy
from urllib.parse import urlparse
import urllib.robotparser
import csv
import lxml 
import pickle

# Que is initialized with our seeds, linkDict will hold urls and their links
# Visited will store all the pages we have been to so we don't do it twice and scraped will store pages scraped
#que = ['https://recipes.fandom.com/wiki/Alfredo_Sauce']
que = ['https://recipes.fandom.com/wiki/Recipes_Wiki']
linkDict = {}
visited = set()
scraped = set()
BASE_DOMAIN = 'recipes.fandom.com' # Base domain to stay in

# Dict for keywords in links we don't want to follow
noVisit = {
	'CreateAccount': '1',
	'UserLogin': '2',
	'edit': '3',
	'CreatePage': '4',
	'&oldid=': '5',
	'Special:Contributions': '6',
	'action=history': '7'  
}

def main():
	# Prompt user to input number of pages to scrape if not an int default set to 5000
	maxPages = input("Enter Number of Pages to Scrape: ")	
	try:
		int(maxPages)
	except:
		print('Not a Number, Default Set to 5000')
		maxPages = 30000 

	
	# Check if our directory for our page files exists
	if not os.path.isdir('pages'):
		os.makedirs('pages')

	#st = time.time()
	pageCount = 0

	# While que is not empty get pages
	while que:
		# If we haven't reached desired pages and haven't visited page attempt to get page
		if len(scraped) < int(maxPages):
			if que[0] not in visited:
				print(pageCount)
				pageCount += getPage(que[0], pageCount)
				time.sleep(1)
			else:
				
				que.pop(0)
		else:
			print('scraped them all')
			break

	# Call function to create matrix and write it to a csv file then print stats			
	createMatrix()
	print(f'Pages Scraped: {pageCount}')
	#print(f'Execution Time: {time.time()-st} seconds')
		
# Function to take url and grab text from page
def getPage(url, pageCount):
	print("Now viewing: " + que[0])
	visited.add(url)

	# Make sure link is not one of the restricted links specified in noVisit
	#if urlparse(url).netloc != BASE_DOMAIN or vetUrl(url) == False:
	if vetUrl(url) == False:
		print('---- Do Not Need ---')
		que.pop(0)
		return(0)

	# Request page if it throws exception or times out pop off que and return
	try:
		page = requests.get(url, timeout=5)		
	except requests.exceptions.RequestException as e:
		print('************--- COULD NOT GET LINK ---************')
		que.pop(0)
		return(0)

	# Check status code pop off que if not 200
	if page.status_code != 200:
		print(f'BAD STATUS CODE: {page.status_code}')
		que.pop(0)
		return(0)

	# Check if we can fetch page with robotparser fuctions
	if checkLink(url) == 0:
		que.pop(0)
		return(0)

	# Grab raw page text as xml format
	rawPage = page.text 
	bs = BeautifulSoup(rawPage, 'lxml')
#
	# Check page content type to make sure it's an html page, seperate with spaces then write page text to file
	if "text/html" in page.headers.get("content-type", ''):
		# Don't want to scrape from category pages or edit pages as they would be duplicates
		try:
			# In fandom this class contains the information on the page we need also grabbing categories list for advanced search
			pageText = bs.find('div', class_='mw-parser-output').get_text(' ')
			
			# Looking for images on page
			imgageList = []
			if bs.find(class_='mw-parser-output').find_all('img') is not None:
				linksList = bs.find(class_='mw-parser-output').find_all('img')
				for imgSrc in linksList:
					imgageList.append(imgSrc.get('src'))

			# Checking if page has Categories
			# CONSIDER REFACTORING SO WE DON'T HAVE EXTRA WORK IN WRITE FUNC
			if bs.find('ul', class_='categories') is not None:
				categories = bs.find('ul', class_='categories').get_text(', ', strip=True)[14:]
			else:
				categories = '' #lil silly but works 
			
			# Call function to write contents of page
			writePage(pageText, url, categories, imgageList)
			scraped.add(url)
			#pageCount += 1
			
		except:
			print('Not recipe Page')
		#scraped.add(url)
	else:
		que.pop(0)
		return(0)

	# Add key to our dictionary
	linkDict[url] = []
	
	# Get a list of all of our out going links from page
	linksList = bs.find(class_='page__main').find_all('a')

	# Make sure our links have the prefix 'http' so we don't get garbage or relative links
	for link in linksList:
		urlStr = link.get('href')
		# Fandom only gives us relative links so create working link
		newLink = 'https://'+BASE_DOMAIN+str(urlStr)
		if str(urlStr).startswith('/wiki') :#and urlparse(urlStr).netloc == BASE_DOMAIN: #and checkLink(url) == 1:		
			linkDict[url].append(newLink)
			if newLink not in visited and newLink not in que:
				que.append(newLink)


	que.pop(0)
	return(1) 

def vetUrl(link):
	vals = [a for b, a in noVisit.items() if b in link]
	if not vals:
		return(True)
	else: 
		return(False)

# Function to write page contents to file in files directory
def writePage(text, fileName, categories, imgageList):
	# Clean up filename and truncate if it's too long
	url = fileName
	fileName = fileName.replace('/', '').replace(':', '')
	if len(fileName) >= 251:
		fileName = fileName[0:251]

	# Open directory to store files then write contents to files	
	with open(f'pages/{fileName}.txt' ,'w') as f:
		f.write(f'Link: {url}\n\n')
		f.write(text.replace('[ ]', ':')) # Get rid of annoying brackets

		# If page has images write source link to file
		if imgageList:
			f.write(f'Images: {imgageList}\n')
		f.write(f'Categories:{categories}') #[:len(categories)-14]}') # Removes text at the end of string('ADD CATEGORY')
		f.close()

# Function to convert our dictionary to adjacency matrix and write it to csv file
def createMatrix():
	# Remove links in key items that are not in our scraped set(for building adjacency matrix)
	for i in linkDict:
		linkDict[i] = set(linkDict[i]).intersection(scraped)
		if not linkDict[i]:
			linkDict[i] = [i]

	# Create list of sets where each set contains a key and a link
	# Then convert the list to a dataframe and use crosstab to get our adjacency matrix
	# ******* CAN REMOVE OR COMMENT OUT LATER KEEPING FOR SCRAPING ***********
	with open('linkDictionary.pickle', 'wb') as handle:
		pickle.dump(linkDict, handle, protocol=-1)
	with open('myque.pickle', 'wb') as h:
		pickle.dump(que, h, protocol=-1)
	with open('visit.pickle', 'wb') as h:
		pickle.dump(visited, h, protocol=-1)
	with open('scraped.pickle', 'wb') as h:
		pickle.dump(scraped, h, protocol=-1)
	linkSets = [(j,k) for j , i in linkDict.items() for k in i]
	df = pandas.DataFrame(linkSets)
	matrix = pandas.crosstab(df[0], df[1])

	# Write adjacency matrix to csv file
	matrix.to_csv('matrix3.csv')
	#print('Sample of Matrix:')
	#print(matrix.iloc[0:9, 0:3])

# Function to read robots file and verify we can access the link
def checkLink(url):
	# Set url for robot parser by grabbing scheme, domain and appending '/robots.txt'
	rp = urllib.robotparser.RobotFileParser()
	domain = urlparse(url).netloc

	rp.set_url(f'{urlparse(url).scheme}://{urlparse(url).netloc}/robots.txt')

	# Attempt to read robots.txt file if not print error message and return
	try:
		rp.read()
	except:
		print('CANNOT READ ROBOTS FILE')
		return(0)
		
	# Make sure we can fetch link according to robots file if not add to bad link dictionary and return 0
	if rp.can_fetch('*', url) == True:
		return(1)
	else:
		print("-------- **** PAGE RESTRICTED ***** ------------")
		return(0)


if __name__ == '__main__':
	main()

