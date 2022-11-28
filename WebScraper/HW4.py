# Antonio Maniscalco
# CS454 HW4
# Instructor: Dr. McCamish

import os, os.path
from whoosh import index
#from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
from whoosh import scoring
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

from whoosh.query import Every

# Class to create our schema
# Class creation taken from documentation https://whoosh.readthedocs.io/en/latest/schema.html
class NewSchema(SchemaClass):
    path = ID(stored=True)
    title = TEXT(stored=True)
    textdata = TEXT(stored=True)
    categories = KEYWORD(stored=True)

# Function to create our index from corpus
def createIndex(dirPath):

	# Create new schema object in index dir, init writer
	schema = NewSchema()
	ix = index.create_in("myIndex",schema)
	writer = ix.writer()
 
 	# Get list of file paths in our directory to index
	filepaths = [os.path.join(dirPath,i) for i in os.listdir(dirPath)]
	
	# Iterate through our list of file paths to index documents
	for path in filepaths:
	    fp = open(path,'r')
	    print(f'Indexing: {path[len(dirPath)+1:]}')
	    text = fp.read()
	    txtToParse = text.split("\n")
	    keyWords = parseFile(txtToParse)
	    mystr=''
	    for k in keyWords:
	    	mystr =mystr+ ' '+ k
	    writer.add_document(path=path, title=path[len(dirPath)+1:], textdata=text, categories=mystr)
	    fp.close()
	writer.commit()

	print(f'Finishing Up Index With {len(filepaths)} Documents...')
	print(f'Schema: {ix.schema}')
	return(ix)

# Function to Grab Categories
def parseFile(fText):
	# Only need last line where categories are
	for line in fText:
		pass

	# Remove the beginning and end 
	last_line = line[12:len(line)-14]
	cats = last_line.split(',')

	return(cats)


# Function to search index from user input Data
def displayResults(ix, queryStr, numReturned):
	#search our new index using bm25 you can add parameter in searcher to select scoring
	#	tf-idf: weighting=scoring.TF-IDF()
	#	frequency: weighting-scoring.Frequency()
	with ix.searcher() as searcher:
		query = QueryParser("textdata", ix.schema).parse(queryStr)
		try:
			res = searcher.search(query, limit=numReturned,terms=True)
			totalResLen = len(res)
			if totalResLen == 0:
				print(f'No Results found for {queryStr}')
				return
			for i in range(numReturned):
				# If returned results is more than found return
				if i not in range(totalResLen):
					return
				print(i, res[i]['title'], str(res[i].score))
		except:
			print(f'No Results found for {queryStr}')


# Function to get and parse user input
def getUserInput(ix):
	while(1):
		# Select type of search enter query and specify number of returned of returned results
		searchType = input('\n\nEnter C for Conjunctive Searching or Enter D for Disjunctive Searching or E to exit: ')
		if searchType == 'E':
			exit(0)
		queryStr = input('Enter a query: ')
		numReturned = input('Enter Number of Returned Results: ')

		# Only need to work on query if search type is conjunctive so replace spaces with ' OR '
		if searchType == 'D':
			queryStr = queryStr.replace(' ', ' OR ')


		print(f'\n\nQuery: {queryStr} | Attempting to Return Top: {numReturned} Results')
		print('----------------------------------------------------------')
		displayResults(ix, queryStr, int(numReturned))

	


def main():

	
	# Check if index directory exists if not create it and build it otherwise open dir
	if not os.path.exists("../src/myIndex"):
		os.mkdir("../src/myIndex")
		ix = createIndex("finalFiles")
	else:
		ix = index.open_dir("myIndex")

	#getUserInput(ix)

if __name__ == '__main__':
	main()

