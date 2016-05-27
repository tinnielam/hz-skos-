# HZ-SKOS*

The Docs Indexer is a simple file which is written in Python, it uses Apache Tika(mapper plugin) to index it's file in a base 64 format. 
The main purpose of this script is to index all documents such as: "pdf,word,xls etc.". After being uploaded you can use.
The Calculator is currently still in development. The main purpose of this script is to calculate the relevance between every single term of the documents and the SKOS concepts.
It's expected result from the Skos terms and every single term from the documents.


#Docs_Indexer

The main index(structure) of the docs_indexer is written as followed :

PUT hzbwnature
{
"mappings" :{ 
"attachment" : {
"properties" : {
"content" : {
"type" : "attachment",
"fields" : {
"content"  : { "term_vector":"yes", "store":"yes" },
"author"   : { "store" : "yes" },
"title"    : { "store" : "yes"},
"date"     : { "store" : "yes" },
"keywords" : { "store" : "yes", "analyzer" : "keyword"},
"name"    : { "store" : "yes" },
"content_length" : { "store" : "yes" },
"content_type" : { "store" : "yes" }
                                      }
                                    }
                                  }
                                }
                              }
                            }  
By using termvectors it will be easier to do analysis such as finding terms and scores.

You can run this query to search for relevant terms which are indexed. See the example below.
Note that if you are running this in sense you will only get the base 64 format returned instead of the normal format.
If you wish to see "the normal format" try to look it up in kibana !

POST /hzbwnature/_search
{
  "query": {
    "query_string": {
      "query": "dijk"
}}}

#cosine similarity Calculator

In order to complete this step please vectorize the fields that you want to calculate. In my case it's the document content, title and the SKOS-concept terms.
After indexing these terms we will move to requesting for these vectors and calculating these fields.

tvjson = es.termvector(index=index_name, doc_type="page",
                                  id=doc_id)
                                  
to get term vectors from the statistics returned we write a function
 
def get_tv_dict(tvjson):
   return dict([ (k, v['term_freq'])  
                 for k,v in tvjson\
                 .get('term_vectors')\
                 .get('page_text')\
                 .get('terms')\
                 .iteritems()])
 
Once we get the term vectors for documents we can calculate the cosine similarity score
Given below is the function to calculate the cosine similarity score of documents given the term vectors



