"""
http.feature.base - 
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

class PipelineComponent:
    """Abstract class for pipeline components."""
    def __init__(self, context):
        """Components can be instantiated with a context."""
        self.context = context
    def send_request(self, request, response):
        """Called when a request is being sent."""
        pass
    def receive_request(self, request, response):
        """Called when a request is received."""
        pass
    def send_response(self, request, response):
        """Called when a response is sent."""
        pass
    def receive_response(self, request, response):
        """Called when a response is received."""
        pass
        
        
## TODO: intermediary hop vs. end
## TODO: allow trapping of errors?