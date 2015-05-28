#!/usr/bin/env python
import sys
import json
import cgi
import time
import os
 
def generate_json(result):
    jsonstr = json.dumps(result)
    print "Content-Type: application/json; charset=UTF-8"
    # Allow query from foreign sites
    print "Access-Control-Allow-Origin: *"
    print "Content-Length: %d"%(len(jsonstr) + 1)
    print
    print jsonstr

def process_form():
    form = cgi.FieldStorage()
    #print >>sys.stderr,"Form",form
    timestamp = str("%.3f"%time.time())
    if not os.path.exists('images'):
        os.mkdir('images')
    filename = "images/I%s.png"%timestamp
    status = os.system("cp test.png %s"%filename)
    #print >>sys.stderr,"Status",status,os.getcwd()
    generate_json({'name': form["name"].value, 'image': filename})

if __name__ == "__main__":
    #print >>sys.stderr,"Start"
    process_form()
    #print >>sys.stderr,"Stop"
