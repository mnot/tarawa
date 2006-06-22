"""
http.header.error - Header error handlers
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

import traceback, sys

class ErrorHandler:
    """
    Base class for error handlers.
    """
    def handle_error(self, context):
        """
        @param context: the object that installed the error handler.
        @type context: instance
        """
        pass
        
class IgnoreErrorHandler(ErrorHandler):
    """
    Ignore all errors.
    """
    pass
    
class RaiseErrorHandler(ErrorHandler):
    """
    Print all errors.
    """
    def handle_error(self, context):
        raise
 
class PrintErrorHandler(ErrorHandler):
    """
    Print all errors.
    """
    def handle_error(self, context):
        (type_, value, tb) = sys.exc_info()
        print "*****", type_, value

class InvalidateErrorHandler(ErrorHandler):
    """
    Mark problem headers as invalid.
    """
    def handler_error(self, context):
        from field_types import FieldValue
        if isinstance(context, FieldValue):
            context.valid = False
    ### TODO: flesh out
        
DefaultErrorHandler = IgnoreErrorHandler
        