# Authors: Antonio Maniscalco, Everette Cooley
# CS 454 Final Project: 'The Gabagool' Recipe Search Engine
# Main Driver file
# Skeleton code provided by Dr. McCamish

# Right now we have a bare bones search engine mostly taken from McCamish on his website. 
# Make changes on the search box, loaded our data with 28k pages, using his searcher but 
#  made a couple changes in the MyWhooshSearcher class.
# For the moment when you search data looks like shit but we will format later once we have full functionality

# Next we need to override the whoosh searcher to implement page rank I will work on that
from flask import Flask, render_template, request, make_response, jsonify
import whoosh
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

@app.route('/complete/', methods=['POST'])
def intermediate():
    req = request.get_json()
    current_q = req['message']
    if current_q == "":
        return make_response(jsonify(''), 200)
    
    current_q = current_q.split()
    current_word = current_q[-1]
    if len(current_word) < 3:
        return make_response(jsonify(''), 200)

    mySearcher = MyWhooshSearcher()
    frequent_term = mySearcher.reader.most_frequent_terms("textdata", number=1, prefix=current_word)
    frequent_term = frequent_term[0][1].decode("ascii")
    res = make_response(jsonify(frequent_term), 200)
    return res

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
    print(f'Category: {cat}')

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
    print(spelling_correction)
 
    return render_template('results.html', query=query, results=zip(urls,contents), categories=categories, spelling_correction=spelling_correction)


# corrects spelling of query
def find_word_corrections(q, reader):
    print("Finding word corrections for: " + q)
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
    print("result = ", result)
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
        self.ix = whoosh.index.open_dir('src/myIndex')
        self.reader = self.ix.reader()
        super(MyWhooshSearcher, self).__init__()
         
    # Function to search takes in user entered query and category selected
    def search(self, queryEntered, category):
        title = list()
        description = list()
        
        # Created our own indexer for now. Could init in constructor later
        indexer = whoosh.index.open_dir("./src/myIndex")
        with indexer.searcher() as search:
            query = MultifieldParser(['title', 'textdata'], schema=indexer.schema)
            query = query.parse(queryEntered)


            # If we have a category we will do conjunctive search for query and category keyword
            if category:
                # Add AND on category to indicate conjunctive search
                category = category + ' AND ' + queryEntered
                catQuery = MultifieldParser(['textdata','categories'], schema=indexer.schema)
                catQuery = catQuery.parse(category)
                results = search.search(catQuery, limit=None)
            else:
                results = search.search(query, limit=None)

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


if __name__ == '__main__':
    global mySearcher
    mySearcher = MyWhooshSearcher()
    mySearcher.index()
    app.run(debug=True)


