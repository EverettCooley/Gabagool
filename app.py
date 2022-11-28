# Authors: Antonio Maniscalco, Everette Cooley
# CS 454 Final Project: 'The Gabagool' Recipe Search Engine
# Main Driver file
# Skeleton code provided by Dr. McCamish

# Right now we have a bare bones search engine mostly taken from McCamish on his website. 
# Make changes on the search box, loaded our data with 28k pages, using his searcher but 
#  made a couple changes in the MyWhooshSearcher class.
# For the moment when you search data looks like shit but we will format later once we have full functionality

# Next we need to override the whoosh searcher to implement page rank I will work on that
#  

from flask import Flask, render_template, url_for, request
import whoosh
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import qparser
from whoosh import scoring

import pickle

 
app = Flask(__name__)

# Open our dictionary containing page rank values
with open('./src/pickles/pageRank.pickle','rb') as handle:
    myDict = pickle.load(handle)

# Open category list
with open("./src/pickles/categoryList.pickle", "rb") as handle:
    categories = pickle.load(handle)

# Render Home Page
@app.route('/', methods=['GET', 'POST'])
def index():
    print("Someone is at the home page.")
    return render_template('welcome_page.html', categories=categories)

@app.route('/my-link/')
def my_link():
    print('I got clicked!')
    return 'Click.' 

# Load results page
@app.route('/results/', methods=['GET', 'POST'])
def results():

    global mySearcher
    if request.method == 'POST':
        data = request.form
    else:
        data = request.args

    # Grab our query and category if selected
    query = data.get('test')
    cat = data.get('category')

    # Create searcher and search
    mySearcher = MyWhooshSearcher()
    titles, descriptions = mySearcher.search(query, cat)


    urls = []
    contents = []

    # Grab descriptions and external link
    for i, description in enumerate(descriptions):
        temp = description.split('\n', 1)
        urls.append(temp[0][6:])
        description = temp[1]
        #print(description)

        current_desc = ''
        for word in query.split():
            result = find_substring(description, word)
            if result != 0:
                current_desc = " ".join(result)
        if current_desc == '':
            description = description.split()
            current_desc = " ".join(description[:20])
        contents.append(current_desc)

        #url = contents.split('\n')

    # print("You searched for: " + query)
    # print("Alternatively, the second box has: " + test)
 
    return render_template('results.html', query=query, results=zip(urls,contents), categories=categories)

def find_substring(base, term):
    base = base.split()
    for i in range(len(base)):
        if base[i].lower() == term.lower():
            return base[i-10:i+10]
    return 0

# ******* NO LONGER IN USE. WILL REMOVE ON FINAL REFACTOR ******
@app.route('/resultList', methods=['GET', 'POST'])
def resultList():
    if request.method == 'POST':
        data = request.form 
    else:
        data = request.args 
    string = data.get('type')
    #print(f'String is: {string}')
    images=''
    with open(f'../HW4/pagesMe/{string}', 'r') as f:
        for line in f:
            if line.startswith("Images:"):
                images = line[9:len(line)-2].strip("'").split(',')
                for img in range(len(images)):
                    try:
                        images[img] = images[img][:images[img].index(".png") + 4]
                    except:
                        try:
                            images[img] = images[img][:images[img].index(".jpg") + 4]
                        except:
                            continue
                      
                
    with open(f'../HW4/pagesMe/{string}', 'r') as f:
        text = f.read()
    return render_template('content.html', text=text, images=images)

def loadImages(f):
    with open(f'../HW4/pagesMe/{string}', 'r') as f:
        for line in f:
            if line.startswith("Images:"):
                images = line[9:len(line)-2].strip("'").split(',')
                for img in range(len(images)):
                    images[img] = images[img][:images[img].index(".png") + 4]
                return(images)
    return(images)

# ******** END OF REMOVE BLOCK *******

# Whoosh searcher using page rank
class MyWhooshSearcher(object):
    """docstring for MyWhooshSearcher"""
    def __init__(self):
        #self.indexer = index.open_dir('myIndex')
        super(MyWhooshSearcher, self).__init__()
         
    # Need to add var for keyword search for andvanced search ***************   
    def search(self, queryEntered, category):
        title = list()
        description = list()
        
        # Created our own indexer for now. Could init in constructor later
        indexer = whoosh.index.open_dir("myIndex")
        with indexer.searcher() as search:
            query = MultifieldParser(['title', 'textdata'], schema=indexer.schema)
            query = query.parse(queryEntered)

            # Set limit to 10 will need to change later as we display 10 per page not 10 total
            results = search.search(query, limit=None, terms=True)
            newDict = {}
            otherDict = {} 

            # Iterate through results to match titles 
            for i in results:
                if i['title'] in myDict:
                    #newDict[i['title']] = myDict[i['title']]
                    #print(f"{i['title']} {myDict[i['title']]}")
                    otherDict[i['title']] = myDict[i['title']]
             
            sortedDict = dict(sorted(otherDict.items(), key=lambda x:float(x[1]), reverse=True))

            # Now dict is sorted add raw text as values
            for i in results:
                sortedDict[i['title']] = i['textdata']

            # Make list from keys and values and return them
            title = list(sortedDict.keys())
            description = list(sortedDict.values())
           # print(f'\nTITLES AFTER: {title}\n')
            
        return title, description

    # ****** DON'T NEED THIS ********
    # ****** SEE HW4 FOLDER FOR BUILDING INDEX *****
    # def index(self):
    #     schema = Schema(id=ID(stored=True), title=TEXT(stored=True), description=TEXT(stored=True))
    #     indexer = create_in('myIndex', schema)
    #     writer = indexer.writer()

    #     writer.add_document(id=u'1', title=u'hello there', description=u'cs hello, how are you')
    #     writer.add_document(id=u'2', title=u'hello bye', description=u'nice to meetcha')
    #     writer.commit()

    #     self.indexer = indexer

# indexer = index()
# search(indexer, 'nice')

if __name__ == '__main__':
    global mySearcher
    mySearcher = MyWhooshSearcher()
    mySearcher.index()
    #title, description = mySearcher.search('hello')
    #print(title)
    app.run(debug=True)


