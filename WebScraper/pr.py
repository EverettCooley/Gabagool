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

""" Uses networkx to create our graph then calculates page rank for-
    each node through 20 iterations"""
# Reference used for code https://www.geeksforgeeks.org/page-rank-algorithm-implementation/?ref=rp
newDict = {}
newQue = [] 
outGoing = {}
myLables = []
with open("linkDictionary.pickle", "rb") as file:
    myDict = pickle.load(file)
    
    gr = nx.DiGraph()
    for i in myDict:
         gr.add_node(i)
         #print(f'Adding {i} node')
    linkSets = [(j,k) for j , i in myDict.items() for k in i]
    #print(linkSets)
    gr.add_edges_from(linkSets)
    weight = 1
   
    nodeNum = gr.number_of_nodes()
    W = nx.stochastic_graph(gr, weight='weight')

    # Starting dictionary with values set to 1/node numbers
    prDict = dict.fromkeys(W, 1.0/nodeNum)

    # Uniform personalization vector
    p = dict.fromkeys(W, 1.0/nodeNum)
    dangleWeights = p 
 
    # Dangling nodes will have an out degree of 1 because every key in dictionary has atleast val of 1
    dangleNodes = [i for i in W if W.out_degree(i, weight='weight') == 1.0]

    for i in range(20):
        # save the previous dictionary to access previous values
        prevPrDict = prDict
        prDict = dict.fromkeys(prevPrDict.keys(), 0)
        # damp factor alpha = 0.85
        danglesum = 0.85 * sum(prevPrDict[i] for i in dangleNodes)

        # Calculate sum for the current iteration
        for n in prDict:
            for node in W[n]:
                prDict[node] += 0.85 * prevPrDict[n] * W[n][node]['weight']
            prDict[n] += danglesum * dangleWeights[n] + (0.15) * p[n]
        

    # Just needed for cleanup of file names
    for i in prDict:
        filename = i.replace('/','').replace(':','')
        if len(filename) >= 251:
            filename = filename[0:251]
        filename = filename + '.txt'
        newDict[filename] = prDict[i]
    print(f'Num of Nodes: {nodeNum}')
   

    # Pickle pagerank dictionary to load in project
    with open('pageRank.pickle','wb') as handle: 
        pickle.dump(newDict, handle, protocol = -1)
