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
from whoosh.qparser import MultifieldParser



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
    titles, descriptions = mySearcher.search(query)

    urls = []
    contents = []
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


    print("You searched for: " + query)
    print("Alternatively, the second box has: " + test)

    spelling_correction = find_word_corrections(query, mySearcher.reader)
    print(spelling_correction)
 
    return render_template('results.html', query=query, results=zip(urls, contents), spelling_correction=spelling_correction)



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

class MyWhooshSearcher(object):
    """docstring for MyWhooshSearcher"""
    def __init__(self):
        self.ix = whoosh.index.open_dir('myIndex')
        self.reader = self.ix.reader()
        super(MyWhooshSearcher, self).__init__()
  
    def search(self, queryEntered):
        title = list()
        description = list()
        indexer = whoosh.index.open_dir("myIndex")
        
        with indexer.searcher() as search:
            query = MultifieldParser(['title', 'textdata'], schema=indexer.schema)
            query = query.parse(queryEntered)

            results = search.search(query, limit=10)
            
            for x in results:
                title.append(x['title'])
                description.append(x['textdata'])
            
        return title, description


if __name__ == '__main__':
    global mySearcher
    mySearcher = MyWhooshSearcher()
    mySearcher.index()
    app.run(debug=True)


