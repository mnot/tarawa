"""
http.server.adapter.base
"""

__license__ = """
Copyright (c) 2003-2006 Mark Nottingham <mnot@pobox.com>

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

import sys, urlparse
from ... import status
from ...message import Request, Response 
from ...feature.common import PipelineComponent
from ...feature.resource_dispatch import MethodDispatcher

METHODS_WITH_BODIES = ['PUT', 'POST']


class ServerAdapter:
    """
    Base class for Server Adapters.
    
    Subclasses should override the serve() method.
    """
    
    def __init__(self, baseResourceClass, baseURI='/'):
        self.baseResource = baseResourceClass(baseURI, None)
        self.baseURI = baseURI
        
    def serve(self):
        """
        Marshal a request into a Request instance and dispatch(); 
        take the Response instance returned and serialize it onto 
        the wire.
        
        Should be overridden.
        """
        pass
        
    def dispatch(self, request):
        """
        Given a Request instance, _dereference the resource
        and hand off to its _handle_request, returning a
        Response instance.
        """        
        method = request.method
        if method == "HEAD":
            request.method == "GET"
        try:
            resource = self.baseResource.dereference(request.uri)
            response = status.OK()
            for stage in resource.pipeline:
                stage.receive_request(request, response)
            for i in xrange(len(self.pipeline), 0, -1):
                self.pipeline[i-1].send_response(request, response)
        except status.Status, response:
            pass
        except Exception, why:
            import traceback
            response = status.InternalServerError()
            response.body = "".join(traceback.format_tb(sys.exc_traceback, 5)) + "\n" + str(why)
        if response.has_content:
            response.headers['Content-Length'] = len(str(response.body)) # TODO: this buffers - allow control
        if method == 'HEAD':
            response.body = ""
        return response

