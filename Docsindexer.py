import os
import sys

# constants, configure to match your environment
HOST = 'http://10.0.2.15:9200'
INDEX = 'hzbwnature'
TYPE = 'attachment'
TMP_FILE_NAME = 'tmp.json'
# for supported formats, see apache tika - http://tika.apache.org/1.4/formats.html
INDEX_FILE_TYPES = ['html','pdf', 'doc', 'docx', 'xls', 'xlsx', 'xml', 'odt', 'ods', 'jpg', 'mp4' ]

def main():

    indexDirectory = raw_input('Index entire directory [Y/n]: ')
        
    if not indexDirectory:
        indexDirectory = 'y'

    if indexDirectory.lower() == 'y':
        dir = raw_input('Directory to index (relative to script): ')
        indexDir(dir)

    else:
        fname = raw_input('File to index (relative to script): ')
        createIndexIfDoesntExist()
        indexFile(fname)

def indexFile(fname):
    print '\nIndexing ' + fname
    createEncodedTempFile(fname)
    postFileToTheIndex()
    os.remove(TMP_FILE_NAME)
    print '\n-----------'

def indexDir(dir):

    print 'Indexing dir ' + dir

    createIndexIfDoesntExist()

    for path, dirs, files in os.walk(dir):
        for file in files:
            fname = os.path.join(path,file)

            base,extension = file.rsplit('.',1)

            if extension.lower() in INDEX_FILE_TYPES:
                indexFile(fname)
            else:
                'Skipping {}, not approved file type: {}'.format(fname, extension)

def postFileToTheIndex():
    cmd = 'curl -X POST "{}/{}/{}" -d @'.format(HOST,INDEX,TYPE) + TMP_FILE_NAME
    print cmd
    os.system(cmd)
    

def createEncodedTempFile(fname):
    import json

    file64 = open(fname, "rb").read().encode("base64")

    print 'writing JSON with base64 encoded file to temp file {}'.format(TMP_FILE_NAME)

    f = open(TMP_FILE_NAME, 'w')
    data = { 'content': file64, 'title': fname }
    json.dump(data, f) # dump json to tmp file
    f.close()


def createIndexIfDoesntExist():
    import urllib2

    class HeadRequest(urllib2.Request):
        def get_method(self):
            return "HEAD"

    # check if type exists by sending HEAD request to index
    try:
        urllib2.urlopen(HeadRequest(HOST + '/' + INDEX + '/' + TYPE))
    except urllib2.HTTPError, e:
        if e.code == 404:
            print 'Index doesnt exist, creating...'

            os.system('curl -X PUT "{}/{}/{}/_mapping/" -d'.format(HOST,INDEX,TYPE) + ''' '{
                                "_default_":{
                                "attachment" : {
                                  "properties" : {
                                    "content" : {
                                      "type" : "attachment",
                                      "fields" : {
                                        "content"  : { "term_vector":"yes", "store":"yes" },
                                        "author"   : { "store" : "yes" },
                                        "title"    : { "store" : "yes"},
                                        "date"     : { "store" : "yes" },
                                        "keywords" : { "store" : "yes", "analyzer" : "keyword" },
                                        "name"    : { "store" : "yes" },
                                        "content_length" : { "store" : "yes" },
                                        "content_type" : { "store" : "yes" }
                                      }
                                    }
                                    }
                                    }}
                                    }
                                  }
                                }
                              }
                            }' ''')    
        else:
            print 'Failed to retrieve index with error code - %s.' % e.code

# kick off the main function when script loads
main()