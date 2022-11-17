Anotnio Maniscalco
CS 454 HW4
README file

Scoring method is set to defaut(bm25) to change go to line 52 under the parameters you can put the following
	tf-idf: weighting=scoring.TF-IDF()
	frequency: weighting-scoring.Frequency()

To run in commandline type 'python3 HW4.py'
You then get the following prompts
	Enter C for Conjunctive Searching or Enter D for Disjunctive Searching or E to exit:
	Enter a query:
	Enter Number of Returned Results:
	
which will infinitely loop unless you enter E on the first prompt to exit