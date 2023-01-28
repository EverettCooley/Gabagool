# Authors: Antonio Maniscalco, Everette Cooley
# CS 454 Final Project: 'The Gabagool' Recipe Search Engine
# Main Driver file
# Skeleton code provided by Dr. McCamish


from flask import Flask, render_template, request, make_response, jsonify
from flask_paginate import Pagination, get_page_parameter
import whoosh
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import qparser
from whoosh import scoring
import pickle
import urllib.request

# sys.path.insert(1, './src/helperCode')
# import t
 
app = Flask(__name__)

# Open our dictionary containing page rank values
with open('./src/pickles/pageRankBig.pickle','rb') as handle:
    myDict = pickle.load(handle)

# Open category list
with open("./src/pickles/categoryListBig.pickle", "rb") as handle:
    categories = pickle.load(handle)

# Render Home Page
@app.route('/', methods=['GET', 'POST'])
def index():
    print("Someone is at the home page.")
    return render_template('welcome_page.html', categories=categories)

@app.route('/complete/', methods=['POST'])
def complete():
    req = request.get_json()
    current_q = req['message']
    if current_q == "":
        return make_response(jsonify(''), 200)
    
    current_q = current_q.split()
    current_word = current_q[-1]
    if len(current_word) < 3:
        return make_response(jsonify(''), 200)

    mySearcher = MyWhooshSearcher()
    try:
        frequent_term = mySearcher.reader.most_frequent_terms("textdata", number=1, prefix=current_word)
        frequent_term = frequent_term[0][1].decode("ascii")
    except IndexError:
        print("string is not in index")
        return make_response(jsonify(''), 400)

    return make_response(jsonify(frequent_term), 200)

@app.route('/my-link/')
def my_link():
    #print('I got clicked!')
    return 'Click.' 

# Handle valid pages. If not redirect to stack overflow
@app.route('/valid/', methods=['GET','POST'])
def valid():
    req = request.get_json()
    url = req['message']
    code = urllib.request.urlopen("https://stackoverflow.com").getcode()
    return make_response(jsonify(code), 200)


# Load results page
@app.route('/results/', methods=['GET', 'POST'])
def results():
    #t.test('hello world')

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
    titles, descriptions, compQ = mySearcher.search(query, cat) 

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

    spelling_correction = find_word_corrections(query, mySearcher.reader)
    # urls = urls[:10]
    # contents = contents[:10]
    try:
        page = int(request.args.get('page',1))
    except ValueError:
        page=1

    # Return 10 results per page
    offset=(page-1)*10
    results = zip(urls[offset:offset+10],contents[offset:offset+10])
    frameWork = 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'

    # Call pagination method to get page info
    pagination = Pagination(page=page,total=len(urls),per_page=10, record_name='results')
    return render_template('results.html', pagination=pagination,query=query, results=results, categories=categories, spelling_correction=spelling_correction, compQ=str(compQ))

# corrects spelling of query
def find_word_corrections(q, reader):
    q = q.strip().split()
    corrections = []
    correction_indexs = set()
    i = 0
    for word in q:
        word = word.lower()
        top_freq, top_word = 0, ""
        matches = reader.terms_within("textdata", text=word, maxdist=1, prefix=1)
        for match in matches:
            term_frequecy = term_freq(match, reader)
            if term_frequecy > top_freq:
                top_freq = term_frequecy
                top_word = match

        if top_word != "" and top_word != word:
            corrections.append(top_word)
            correction_indexs.add(i)
        i+=1

    result = ""
    if len(corrections) > 0:
        result = 'Did you mean: " '
        for i in range(len(q)):
            if i in correction_indexs:
                result += str(corrections.pop(0)) + " "
            else:
                result += str(q[i]) + " "
        result += '" ?'
    return result


# helper function of find_word_corrections
def term_freq(term, reader):
    return reader.frequency("textdata", term)

def find_substring(base, term):
    base = base.split()
    for i in range(len(base)):
        if base[i].lower() == term.lower():
            return base[i-10:i+10]
    return 0



# Whoosh searcher using page rank
class MyWhooshSearcher(object):
    """docstring for MyWhooshSearcher"""
    def __init__(self):
        #self.indexer = index.open_dir('myIndex')
        self.ix = whoosh.index.open_dir('src/myIndexBig')
        self.reader = self.ix.reader()
        super(MyWhooshSearcher, self).__init__()
         
    # Function to search takes in user entered query and category selected
    def search(self, queryEntered, category):
        title = list()
        description = list()
        
        # Make query multi field searcher and make disjunctive search
        indexer = whoosh.index.open_dir("./src/myIndexBig")
        with indexer.searcher() as search:
            if queryEntered:
                query = MultifieldParser(['title', 'textdata'], schema=indexer.schema)
                query = query.parse(queryEntered)
                #query = Or(query)
            else:
                query = ''


            # If we have a category we will do conjunctive search for query and category keyword
            if category:
                # Only searching keyword field for categories then conjunctive search with query
                catQuery = MultifieldParser(['categories'], schema=indexer.schema)
                catQuery = catQuery.parse(category) 
                if queryEntered:
                    query = And([catQuery, query])
                else:
                    query = catQuery
                results = search.search(query, limit=None)
            else:
                results = search.search(query, limit=None)

            newDict = {}
            prScoresDict = {} 

            # Iterate through results to match titles 
            for i in results:
                if i['title'] in myDict:
                    prScoresDict[i['title']] = myDict[i['title']]
             
            sortedDict = dict(sorted(prScoresDict.items(), key=lambda x:float(x[1]), reverse=True))

            # Now dict is sorted add raw text as values
            for i in results:
                sortedDict[i['title']] = i['textdata']

            # Make list from keys and values and return them
            title = list(sortedDict.keys())
            description = list(sortedDict.values())
            
        return title, description, query

    # ****** DON'T NEED THIS WAS USED FOR BUILDING INDEX ********
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
    app.run(debug=True)


