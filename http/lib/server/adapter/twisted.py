"""
http.server.adapter.twisted
"""

__license__ = """
Copyright (c) 2006 Mark Nottingham <mnot@pobox.com>

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

from .base import ServerAdapter

class TarawaReceiver():
    def receiveLine(self, line):
        ... if no current context, create a message
            ... read in the header line
        ... else if in header context, buffer
            ... if done headers, write to .headers, then switch to body mode
        ... else if in body context, write to body_iter
            ... doing the proper byte counting, closing the message down when done.

class Twisted(ServerAdapter):
    """twisted HTTP Server Adapter"""
    def __init__(self, baseResourceClass, baseURI='',):
        ServerAdapter.__init__(self, baseResourceClass, baseURI)
        self.offset = len(urlparse.urlsplit(baseURI)[2].split('/')) - 1
    
    def dispatch(self, request):
        request.uri_path = request.uri[self.offset:]
        return ServerAdapter.dispatch(self, request)

    def serve(self):
        
        
        
        import os
        linesep = "\r\n"
        request = Request()
        request.headers.parseCGI()
        request.method = os.environ['REQUEST_METHOD']
        request.uri = os.environ['REQUEST_URI']
        if request.method in METHODS_WITH_BODIES:
            request.body = sys.stdin.read()
        response = self.dispatch(request)
        sys.stdout.write("Status: %s %s%s" % (response.status_code, response.status_phrase, linesep) )
        sys.stdout.write(str(response.headers))
        sys.stdout.write(linesep)
        if response.has_body and response.has_content:
            sys.stdout.write(response.body)