#!/usr/bin/env python
import sys
import json
import cgi
 
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
    # Sanitize input to prevent XSS injection
    name = cgi.escape(form.getfirst("name"))
    generate_json({'name': name})

if __name__ == "__main__":
    #print >>sys.stderr,"Start"
    process_form()
    #print >>sys.stderr,"Stop"
