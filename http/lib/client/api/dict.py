"""
http.client.api.dict - 
"""

__license__ = """
Copyright (c) 2004-2006 Mark Nottingham <mnot@pobox.com>

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

#TODO: polling interface / non-blocking update
#TODO: expect / continue
#TODO: ranges -  web['foo'][:23]?
#TODO: define and use URI object

from .. import status
from ...message import Request, Response

class Dict(Client):
    """HTTP Client as a dictionary of Representations."""    
    def __getitem__(self, key):
        "GET"
        request = Request()
        request.uri = key
        request.method = "GET"
        response = self._dereference(request)
        return response
        
    def __setitem__(self, key, item):
        "PUT"
        request = Request(representation=item)
        request.uri = key
        request.method = "PUT"
        response = self._dereference(request)
        
    def __delitem__(self, key):
        "DELETE"
        request = Request()
        request.uri = key
        request.method = "DELETE"
        response = self._dereference(request)
        
    def __call__(self, uri, representation):
        "POST"
        request = Request(representation=representation)
        request.uri = uri
        request.method = "POST"
        response = self._dereference(request)
        return response.representation

    def __getattr__(self, attr):
        "Extension Methods"
        if attr == attr.upper():
            return self._extension_method(self, attr)
        else:
            try:
                return self.__dict__[attr]
            except KeyError:
                raise AttributeError

    class _extension_method: 
        """
        Allows arbitrary HTTP methods to be called with (uri, representation?) args.
        """
        def __init__(self, dictionary, attr):
            self.dict = dictionary
            self.method = attr
        def __call__(self, uri, representation=None):
            request = Request(representation=representation)
            request.uri = uri
            request.method = self.method
            return self.dict.dereference(request)
