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
    # Sanitize input to prevent XSS injection
    name = cgi.escape(form.getfirst("name"))
    #print >>sys.stderr,"Form",form
    chart = {
        "data": [[1,1],[2,2],[3,1]],
        "options": { 
            "title":"Title",
            "axes": { "yaxis": { "min":-1, "max":5 }},
            "series": [{"color": "#5FAB78"}],
            }
        }
    generate_json({'name': name, 'chart': chart})

if __name__ == "__main__":
    #print >>sys.stderr,"Start"
    process_form()
    #print >>sys.stderr,"Stop"
