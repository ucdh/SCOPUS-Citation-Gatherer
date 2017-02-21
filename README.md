#SCOPUS Citation Finder

A Python 3 script which gathers citation data for research repositories from http://www.scopus.com.

The script uses two Elsevier SCOPUS APIs: the [SCOPUS Search API](http://api.elsevier.com/documentation/SCOPUSSearchAPI.wadl) and the [Abstract Retrieval API](http://api.elsevier.com/documentation/AbstractRetrievalAPI.wadl). Firstly, it identifies articles in SCOPUS that have referenced your research repository. It then examines each articles and pulls out metadata about the relevant citations.

To run:

1. Clone or download the repository
2. Create an apikey at http://dev.elsevier.com/myapikey.html and add this to the config.py file
3. Add repository codes to the reposistory list in config.py (NZ repository codes can be found in the New Zealand Repository Codes text file)
4. Navigate to the directory and run the get_articles.py

The script writes the ids, urls, titles, and authors of the referencing and referenced articles to a tab-delimitered text file

**Note:** Since the Elsevier Scopus APIs is often updated, changes to this code will need to be made over time to ensure that it still works. We welcome contributions, pull requests, and any improvements. 

Example data can be found here: [Scopus Results 5-09-2016](https://figshare.com/account/projects/14855/articles/3806307)




