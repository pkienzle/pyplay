#!/usr/bin/env python
import sys
import cgi
 
def generate_html(name):
    print """\
Content-type: text/html

<p>Hello, %(name)s!</p>
""" % {"name": name}

def process_form():
    form = cgi.FieldStorage()
    print >>sys.stderr,"Form",form
    # Sanitize input to prevent XSS injection
    name = cgi.escape(form.getfirst("name"))
    generate_html(name)

if __name__ == "__main__":
    print >>sys.stderr,"Start"
    process_form()
    print >>sys.stderr,"Stop"
