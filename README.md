#SCOPUS Citation Finder

A script which returns citation data for New Zealand research repositories from (http://www.scopus.com).

The script uses two Elsevier SCOPUS APIs: the SCOPUS Search API and the Abstract Retrieval API. Firstly, it identifies articles in SCOPUS that have referenced a research repository article. It then examines these articles and pulls out the relevant citation data.

To run:

1. Clone or download the repository
2. Add an api key to the 

To run, navigate to script folder in command prompt and type:


python "get referenced articles.py" > results.csv
