#Copyright 2016 Lucy-Jane Walsh
#Licensed under the Apache License, Version 2.0;
#You may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License

import requests, json, re, csv, time
from config import apikey, repositories
import codecs

#creates output file (results.txt)
output_file = codecs.open("results.txt", "w",'utf-8')

'''
A function which runs a search query in SCOPUS. Request number is
set to 100. Start can be adjusted if there are more than 100 records
'''
def search(query,start):    
    articles = requests.get("http://api.elsevier.com/content/search/index:SCOPUS?query=" + query + '&count=100' + '&start=' + str(start),headers={'Accept':'application/json','X-ELS-APIKey':apikey})
    json = articles.json()
    return json

'''
A function that takes a given article id (scopus_id) 
and retrieves the article's json
'''
def get_article_info(id):
    article_info = requests.get("http://api.elsevier.com/content/abstract/scopus_id/" + id,headers={'Accept':'application/json','X-ELS-APIKey':apikey})
    json = article_info.json()
    return json
    

'''
A function which finds the title, authors, link, and id for
a referencing article and any cited articles that
meet the regex expression ("/repository number/some number").
The information is written to a tab-delimitered
text file (results.txt)
'''
def find_referenced_articles(id,article_info,repository):
    referencing_article_title = article_info['abstracts-retrieval-response']['coredata']['dc:title']
    referencing_article_title = referencing_article_title
                
    try:
        referencing_authors = article_info['abstracts-retrieval-response']['coredata']['dc:creator']['author']    
        referencing_author_lst = [author['ce:indexed-name'] for author in referencing_authors]
        referencing_article_authors = ", ".join(referencing_author_lst)
    except:
        referencing_article_authors = "No author listed"
                
                
    referencing_article_link_json = article_info['abstracts-retrieval-response']['coredata']['link']
    referencing_article_date = article_info['abstracts-retrieval-response']['coredata']['prism:coverDate']
    
    
    
    try:
        referencing_locations = article_info['abstracts-retrieval-response']['affiliation'] 
        if isinstance(referencing_locations,dict):
            name = referencing_locations['affilname']
            city = referencing_locations['affiliation-city']
            country = referencing_locations['affiliation-country']
            referencing_article_locations = name + ": " + city + ", " + country
        else:
            referencing_article_locations_lst = []
            for location in referencing_locations:
                name = location['affilname']
                city = location['affiliation-city']
                country = location['affiliation-country']
                new_location = name + ": " + city + ", " + country 
                referencing_article_locations_lst.append(new_location)
            referencing_article_locations = "; ".join(referencing_article_locations_lst)        
    except:
        referencing_article_locations= "No locations listed"    
    
    for link in referencing_article_link_json:
        if link['@rel'] == 'scopus':
            referencing_article_url = link['@href'].replace('&amp;','&')
                
    
    for reference in article_info['abstracts-retrieval-response']['item']['bibrecord']['tail']['bibliography']['reference']:    
        
        #finds url/handle
        url = None        
        try:
            url = reference['ref-info']['ref-website']['ce:e-address']['$']
        except:
            url = None
        
        if url != None:
            regex = '\/' + repository + '\/\d{1,6}'
            match = re.search(regex,url)
            
            if match != None:
                #finds reference id
                reference_id = reference['ref-info']['refd-itemidlist']['itemid']['$']
                    
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
                                        
                author_lst = ', '.join(author_lst)
                                                        
                '''                          
                returns relavent information. Replaces commas in titles to semi-colons 
                so csv puts them in one cell. Turns author_lst into a string
                '''
                                        
                row = '    '.join([id,referencing_article_url,referencing_article_title,referencing_article_authors,referencing_article_locations, referencing_article_date,reference_id,url,title,author_lst])
                
                output_file.write(row + '\n')

#list to store the article ids gathered returned by the search() function                
article_ids = []

'''
A function which runs a search in SCOPUS for a
given repository. Start is set by the user
and 100 is added each time the query is run. 
When the query returns no values, an exception
is reached and the function returns the list 
of article ids
'''

def run_query(repository,start):
    query = "website('" + repository + "')"    
    articles = search(query,start)        
    try:
        for article in articles['search-results']['entry']:        
            id = article['dc:identifier']
            article_ids.append(id)    
        start += 100
        run_query(repository,start)
    except:
        pass
            

'''
Runs the search(), get_article_info() 
and find_referenced_articles() functions 
for each repository in the repository list.
'''
for repository in repositories:
    articles = run_query(repository,0)    
    for id in article_ids:        
        info = get_article_info(id)
        find_referenced_articles(id,info,repository)
    #empties the article_id list
    article_ids = []
output_file.close()
    
    