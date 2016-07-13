import requests, json, re, csv, time
from config import apikey, repositories
import random

repositories = ['10092']
'''
function which runs a search query in scopus. Request number is
set to 100 and start can be adjusted if there are more records
'''
def search(query,start):	
	articles = requests.get("http://api.elsevier.com/content/search/index:SCOPUS?query=" + query + '&count=100' + '&start=' + str(start),headers={'Accept':'application/json','X-ELS-APIKey':apikey})
	json = articles.json()
	return json

'''
function takes a given article id (scopus_id) and returns
the article json
'''
def get_article_info(id):
	article_info = requests.get("http://api.elsevier.com/content/abstract/scopus_id/" + id,headers={'Accept':'application/json','X-ELS-APIKey':apikey})
	json = article_info.json()
	return json
	

'''
function which finds the title, authors, link, and ID for
a referencing article and any referenced articles that
meet the regex expression (/repository/some number)
'''
def find_referenced_articles(id,article_info,repository):
	try:
		referencing_article_title = article_info['abstracts-retrieval-response']['coredata']['dc:title']
		referencing_article_title = referencing_article_title.replace(',',';')
				
		referencing_article_authors = article_info['abstracts-retrieval-response']['coredata']['dc:creator']['author']
		referencing_author_lst = [author['ce:indexed-name'] for author in referencing_article_authors]
		referencing_authors = ";".join(referencing_author_lst)	
				
				
		referencing_article_link_json = article_info['abstracts-retrieval-response']['coredata']['link']
		referencing_article_url = ''
		for link in referencing_article_link_json:
			if link['@rel'] == 'scopus':
				referencing_article_url = link['@href'].replace('&amp;','&')
				
		for reference in article_info['abstracts-retrieval-response']['item']['bibrecord']['tail']['bibliography']['reference']:		
			#finds url/handle
			try:
				url = reference['ref-info']['ref-website']['ce:e-address']['$']
				regex = '\/' + repository + '\/\d{1,6}'
				match = re.search(regex,url)
				if match!= None:
					try:
						#finds reference id
						reference_id = reference['ref-info']['refd-itemidlist']['itemid']['$']
					except:
						reference_id = None
					
					#finds title
					try:
						title = reference['ref-info']['ref-sourcetitle']
					except:
						try:
							title = reference['ref-info']['ref-title']['ref-titletext']
						except:
							try:
								title = reference['ref-info']['ref-text']
							except:
								try:
									title = reference['ref-fulltext']
								except:
									title = 'No title listed'
					try:
						#finds authors
						authors = reference['ref-info']['ref-authors']['author']
									
						#stores author json as list
						author_lst = []
							
						try:
							#if only one author (eg 'ce:indexed-name' is a key in authors, then add to list
							author_lst.append(authors['ce:indexed-name'])
						except:
							#otherwise loops through authors and adds each name to list
							for author in authors:				
								author_lst.append(author['ce:indexed-name'])
					except:
						#if can't find any authors, replaces list with 'No author listed' message
						author_lst = ['No author listed']
								
					author_lst = '; '.join(author_lst)
								
					#dealing with a bunch of encoding issues
					title = title.replace(u'\u201d',u'"')
					title = title.replace(u'\u2013',u'-')
					title = title.replace(u'\u0101',u'a')
					title = title.replace(u'\u2018',u"'")
					title = title.replace(u'\u2019',u"'")
					title = title.replace(",",";")
						
					'''returns relavent information. Replaces commas in titles to semi-colons 
					so csv puts them in one cell. Turns author_lst into a string'''
								
					print ','.join([id,referencing_article_url,referencing_article_title,referencing_authors,reference_id,url,title,author_lst])
			except:
				pass
	except:
		print id

ids = []

'''
Function which runs a search in SCOPUS for a
given repository. Start is set to 0 and 100 
is added each time the query is run. When
the query returns no values, an exception
is reached and the function returns all 
the ids

This is basically a way of getting
around the fact that the SCOPUS API will only
return a max 200 results at a time.
'''
def run_query(repository,start):
	query = "website('" + repository + "')"	
	articles = search(query,start)		
	try:
		for article in articles['search-results']['entry']:		
			id = article['dc:identifier']
			ids.append(id)	
		start += 100
		run_query(repository,start)
	except:
		pass
			

#runs search for each research repository
for repository in repositories:
	articles = run_query(repository,0)	
	for id in ids:		
		info = get_article_info(id)
		find_referenced_articles(id,info,repository)	
	id = []