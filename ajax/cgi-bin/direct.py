#!/usr/bin/env python
import sys
import cgi
 
def generate_html(name):
    print """\
Content-type: text/html

<html>
<body>
<title>Test CGI response</title>
<p>Hello, %(name)s!</p>
</hr>
<a href="../index.html">Back to form</a>
</body>
</html>
""" % {"name": name}

def process_form():
    form = cgi.FieldStorage()
    #print >>sys.stderr,"Form",form
    # Sanitize input to prevent XSS injection
    name = cgi.escape(form.getfirst("name"))
    generate_html(name)

if __name__ == "__main__":
    process_form()
