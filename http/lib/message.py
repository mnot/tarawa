"""
http.message - HTTP message constructs.
"""

__license__ = """
Copyright (c) 2001-2006 Mark Nottingham <mnot@pobox.com>

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

from .header import collection

linesep = "\r\n" #TODO: out to a utility lib

class _BodyString(object):
    "An Entity Body, as a string"
    def __get__(self, obj, objtype):
        if obj._body is None:
            if obj._body_iter is None:
                return None
            else:
                obj._body = ''.join(obj._body_iter)
        return obj._body
    def __set__(self, obj, value):
        del obj.body_iter
        obj._body = value
    def __delete__(self, obj):
        obj._body = None

class _BodyIterator(object):
    "An Entity Body, as an iterator"
    def __get__(self, obj, objtype):
        if obj._body_iter is None:
            if obj._body is None:
                return None
            else:
                obj._body_iter = self._stringGenerator(obj._body)
        return obj._body_iter
    def __set__(self, obj, value):
        del obj.body
        obj._body_iter = value
    def __delete__(self, obj):
        obj._body_iter = None
    def _stringGenerator(self, value):
        yield value
        
class _HasContentFlag(object):
    "Indicates whether the object has any body content presently."
    def __get__(self, obj, objtype):
        if obj._body_iter is None and obj._body is None:
            return False
        else:
            return True

class Representation(object):
    """
    The abstract representation corresponding to an HTTP message.
    
    @ivar headers: metadata
    @type headers: headers.collection.HeaderDict
    @ivar body: content
    @type body: string
    @ivar body_iter: content
    @type body_iter: interator
    """
    def __init__(self, message=None):
        message = message or Message()
        self.body, self.body_iter = message.body, message.body_iter
        self.headers = message.headers #FIXME: weed out non-Entity headers

class RepresentationType(object):
    def __get__(self, obj, objtype=None):
        return Representation(obj)


class Message(object):
    """
    Base class for HTTP messages
    
    @cvar proto_version: HTTP protocol version (e.g., "HTTP/1.1")
    @type proto_version: string
    @ivar headers: HTTP headers
    @type headers: headers.collection.HeaderDict
    @ivar body: HTTP entity body
    @type body: string
    @ivar body_iter: HTTP entity body
    @type body_iter: iterator
    @ivar has_content: whether the body actually contains anything (read-only)
    @type has_content: Boolean
    @ivar representation: the representation conveyed by the message
    @type representation: Representation
    """
    proto_version = None
    has_content = _HasContentFlag()
    body, _body = _BodyString(), None
    body_iter, _body_iter = _BodyIterator(), None    
#    representation = RepresentationType()  ## does this modify in place (headers)?
    def __init__(self):
        self.headers = collection.HeaderValues()

class RequestLine(object):
    def __get__(self, obj, objtype=None):
        return "%s %s %s" % (obj.method, obj.uri, obj.proto_version)
    def __set__(self, obj, value):
        l = value.strip().split(" ") #TODO: should be multiple spaces; use a regex
        obj.method = l[0]
        obj.uri = "%20".join(l[1:-1])
        obj.proto_version = l[-1]
        
class Request(Message):
    """
    HTTP request message
    
    @cvar method: HTTP method
    @type method: string
    @cvar uri: request-URI
    @type uri: string
    """
    method = None
    uri = None
    request_line = RequestLine()
    def __str__(self):
        o = [self.request_line, str(self.headers), '']
        if self.body != None:  ###TODO: switch to iterator, hascontent
            o.append(self.body)
        return linesep.join("o")


class Response(Message):
    """
    HTTP response message
    
    @cvar status_code: three-digit HTTP response status code
    @type status_code: int 
    @cvar status_phrase: human-readable response status phrase
    @type status_phrase: string 
    """

    status_code = None
    status_phrase = None 
    class _status_line(object):
        def __get__(self, obj, objtype=None):
            return "%s %s %s" % (obj.proto_version, obj.status_code, obj.status_phrase)
        def __set__(self, obj, value):
            l = value.strip().split(" ") #TODO: should be multiple spaces; use a regex
            obj.proto_version = l[0]
            obj.status_code = l[1]
            obj.status_phrase = " ".join(l[2:])
    status_line = _status_line()
    
    def __str__(self):
        o = [self.status_line, str(self.headers), '']
        if self.has_body and self.body != None:  ##TODO: hascontent, iterator
            o.append(self.body)
        return linesep.join(o)
