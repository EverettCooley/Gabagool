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


app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    print("Someone is at the home page.")
    return render_template('welcome_page.html')

@app.route('/my-link/')
def my_link():
    print('I got clicked!')
    return 'Click.' 

@app.route('/results/', methods=['GET', 'POST'])
def results():
    global mySearcher
    if request.method == 'POST':
        data = request.form
    else:
        data = request.args

    query = data.get('test')
    test = data.get('test')
    mySearcher = MyWhooshSearcher()
    titles, description = mySearcher.search(query)
    print("You searched for: " + query)
    print("Alternatively, the second box has: " + test)
 
    return render_template('results.html', query=query, results=zip(titles, description))


class MyWhooshSearcher(object):
    """docstring for MyWhooshSearcher"""
    def __init__(self):
        #self.indexer = index.open_dir('myIndex')
        super(MyWhooshSearcher, self).__init__()
         
        
    def search(self, queryEntered):
        title = list()
        description = list()
        
        # Created our own indexer for now. Could init in constructor later
        indexer = whoosh.index.open_dir("myIndex")
        with indexer.searcher() as search:
            query = MultifieldParser(['title', 'textdata'], schema=indexer.schema)
            query = query.parse(queryEntered)

            # Set limit to 10 will need to change later as we display 10 per page not 10 total
            results = search.search(query, limit=10)
            
            # Getting list of titles and page content
            for x in results:
                title.append(x['title'])
                description.append(x['textdata'])
            
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


