"""
http.client.adapter.httplib - 
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

from httplib import HTTP
from urlparse import urlparse
from ..feature.base import PipelineComponent
from .. import status

class Httplib(PipelineComponent):
    """Client-side component for getting representations off the network, the traditional way."""
    def __init__(self, context):
        self.client = context
        self.user_agent = getattr(self.client, "UserAgent", "Python http (%s)" % __version__)
    
    def send_request(self, request, response):
        h = HTTP(urlparse(request.uri)[1])  #TODO: split out port, userinfo
        h.putrequest(request.method, request.uri)
        for field_name, field_value in request.representation.headers.items():
            if field_name == "Content-Length": continue
            h.putheader(field_name, field_value.string)
        if request.representation.has_body:
            h.putheader('Content-Length', str(len(request.representation.body))) #FIXME: hmm. accesses body. options?
        h.putheader('User-Agent', self.user_agent) # FIXME: use header dict, don't override
        h.endheaders()
        if request.representation.has_body:
            h.send(request.representation.body) #FIXME: use iterator?
        status_code, status_phrase, headers = h.getreply()
        response_type = status.lookup.get(status_code, None)
        if response_type is not None:
            response.__class__ = response_type
        response.status_code = status_code
        response.status_phrase = status_phrase
        response.representation.headers.parseMessage(headers)  #FIXME: split entity and message hdrs
        response.representation._body_iter = h.getfile() #FIXME: iterator, shouldn't have to do this _ ...
        if not isinstance(response, status.Successful):
            raise response

