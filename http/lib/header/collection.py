"""
http.header.collection - collections of HTTP headers
"""

__license__ = """
Copyright (c) 1999-2006 Mark Nottingham <mnot@pobox.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__revision__ = "$Id: filelist.py,v 1.15 2002/11/19 13:12:27 akuchling Exp $"

import re, os
from UserDict import UserDict
from .registry import get_field_name, new_field, field_map
from .field_types import FieldValue, UnfoldableFieldValue, UnknownHeader
from . import error

CRLF = re.compile("\r?\n")
LWS = re.compile("\r?\n[ \t]+")
linesep = "\r\n" 

        
class Headers(UserDict):
    def __init__(self, dict=None, error_handler=None):
        UserDict.__init__(self, dict)
        self.error_handler = error_handler or error.RaiseErrorHandler()
    
    def parseString(self, header_string):
        """
        Parse a string into a dictionary.
        
        @param header_string: HTTP headers, separated by newlines
        @type header_string: string
        """
        for line in CRLF.split(LWS.sub(" ", header_string)):
            try:
                fn, f_value = line.split(":", 1)
            except:
                if not line: continue
                self.error_handler.handle_error(self)        
            f_name = get_field_name(fn.strip())
            if self.data.has_key(f_name):
                self.data[f_name] += ", " + f_value.strip()
            else:
                self.data[f_name] = f_value.strip()

    def __str__(self):
        o = []
        for f in self.data.items():
            try:
                o.append("%s: %s" % f)
            except:
                self.error_handler.handle_error(self)
            o.append("")
        return linesep.join(o)

    def __getitem__(self, key):
        return self.data[get_field_name(key)]
    
    def __setitem__(self, key, value):
        self.data[get_field_name(key)] = value

    def __delitem__(self, key):
        del self.data[get_field_name(key)]

    def has_key(self, key):
        return self.data.has_key(get_field_name(key))
    
    def get(self, key, failobj=None):
        return self.data.get(get_field_name(key), failobj)


class HeaderValues(Headers):
    def __getitem__(self, key):
        key = get_field_name(key)
        return field_map.get(key, UnknownHeader)._parse(self.data[key])

    def __setitem__(self, key, value):        
        key = get_field_name(key)
        self.data[key] = field_map.get(key, UnknownHeader)._asString(value)

    def get(self, key, failobj=None):
        pass
    

#####################################################################
    
class HeaderDict(UserDict):
    """
    A dictionary of FieldValue instances, keyed by header name
    (case-insensitive).
    """
    # TODO: header typing (e.g., entity, resource) and ordering
    
    def __init__(self, dict=None, error_handler=None, **kwargs):
        UserDict.__init__(self, dict, **kwargs)
        self.error_handler = error_handler or error.DefaultErrorHandler()
    
    def parseString(self, headers):
        """
        Parse a string into a dictionary.
        
        @param headers: HTTP headers, separated by newlines
        @type headers: string
        """
        for line in CRLF.split(LWS.sub(" ", headers)):
            if not line: continue
            try:
                fn, f_value = [f.strip() for f in line.split(":", 1)]
                f_name = get_field_name(fn)
                if self.data.has_key(f_name):
                    if isinstance(self.data[f_name], UnfoldableFieldValue):
                        self.data[f_name].value += self.data[f_name]._parse(f_value)
                    else:
                        self.data[f_name].string += ", " + f_value
                else:
                    self.data[f_name] = new_field(f_name, self.error_handler)
                    self.data[f_name].string = f_value
            except:
                self.error_handler.handle_error(self)

    def parseMessage(self, message):
        """
        Parse an rfc822.Message instance.
        
        @param message: RFC822 message containing HTTP headers
        @type message: L{rfc822.Message} instance
        """
        for line in message.headers:
            if not line: continue
            try:
                fn, f_value = [f.strip() for f in line.split(":", 1)]
                f_name = get_field_name(fn)
                if self.data.has_key(f_name):
                    if isinstance(self.data[f_name], UnfoldableFieldValue):
                        self.data[f_name].value += self.data[f_name]._parse(f_value)
                    else:
                        self.data[f_name].string += ", " + f_value
                else:
                    self.data[f_name] = new_field(f_name, self.error_handler)
                    self.data[f_name].string = f_value
            except:
                self.error_handler.handle_error(self)
                
    def parseCGI(self, env=None):
        """
        Parse request headers from the environment (or other 
        similarly structured dictionary), as per the CGI specification.
        
        @param env: environment variables (defaults to current environment)
        @type env: dict
        """
        if env is None:
            env = os.environ
        for f_name, f_value in env.items():
            if f_name in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
                pass
            elif f_name[:5] == 'HTTP_':
                f_name = f_name[5:].replace('_', '-')
            else:
                continue
            try:
                f_name = get_field_name(f_name)
                self.data[f_name] = new_field(f_name, self.error_handler)
                self.data[f_name].string = f_value
            except:
                self.error_handler.handle_error(self)
                
    def parseDict(self, dictionary):
        """
        Iterate through a dict's items and parse each as a header.
        
        @param dictionary: HTTP header field-names and field-values
        @type dictionary: dict
        """
        for fn, f_value in dictionary.items():
            f_name = get_field_name(fn)
            try:
                self.data[f_name] = new_field(f_name, self.error_handler)
                self.data[f_name].string = f_value
            except:
                self.error_handler.handle_error(self)
            
    def putheaders(self, httpobj):
        """
        Put contained headers into httpobj using its putheader() method. 
        
        @param httpobj: what to put the headers into
        @type httpobj: httpobj
        """
        for f_name, f_value in self.data.items():
            httpobj.putheader(f_name, f_value.string)

    def __str__(self):
        o = []
        for f_name, f_value in self.data.items():
            try:
                if isinstance(f_value, UnfoldableFieldValue):
                    for value in f_value.value:
                        o.append("%s: %s" % (f_name, f_value._asString([value])))
                else:
                    o.append("%s: %s" % (f_name, f_value.string))
            except:
                self.error_handler.handle_error(self)
            o.append("")
        return linesep.join(o)
            
    def __getitem__(self, key):
        f_name = get_field_name(key)
        if not self.data.has_key(f_name):
            return new_field(f_name, self.error_handler)
        else:
            return self.data[f_name]
            
    def __setitem__(self, key, value):
        f_name = get_field_name(key)
        if isinstance(value, FieldValue):
            self.data[f_name] = value
        else:
            self.data[f_name] = new_field(f_name, self.error_handler, value=value)

    def __delitem__(self, key):
        del self.data[get_field_name(key)]

    def has_key(self, key):
        return self.data.has_key(get_field_name(key))
    
    def get(self, key, failobj=None):
        return self.data.get(get_field_name(key), failobj)

def test(headers):
    for name, value in hdrs.items():
        print "%s:" % name
        print "\t%s\n\t%s\n\t%s" % \
          (value.__class__.__name__, value.string, repr(value.value))
        print "\t%s" % value.string
        print
    print str(headers)


if __name__ == '__main__':
    import fields # populates the registry
    hdrs = Dict()
    hdrs.error_handler = error.RaiseErrorHandler()
    if os.environ.has_key('GATEWAY_INTERFACE'):
        import cgitb 
        cgitb.enable()
        hdrs.parseCGI()
        print "Content-Type: text/plain"
        print
        test(hdrs)
    else:
        import sys
        hdrs.parseString(sys.stdin.read())
        test(hdrs)
        