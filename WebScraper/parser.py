# Gathers Categories

# iterates through files collected
# generates list of categories then pickles the list 
# to be used in main project
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
from numpy import genfromtxt
import networkx as nx 
import matplotlib.pyplot as plt
#import scipy
 
counter = 0
filePaths = [os.path.join('pages/', i) for i in os.listdir('pages')]
categories = []
for file in filePaths:
	with open(file) as fp:
		for line in fp:
			pass
		last_line = line[12:len(line)-14]
		cats = last_line.split(',')
		for category in cats:
			if category not in categories:
				categories.append(category)

print(len(categories))
categories.sort()

with open("categoryList.pickle", "wb") as handle:
	pickle.dump(categories, handle, protocol = -1)
