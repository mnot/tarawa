"""
http.header.registry - HTTP Header Field Registry 

This module provides a metaclass and functions that together implement a 
centralised registry of HTTP header field names and the implementations
for their values.
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

field_map = {}
header_name_map = {}

def get_field_name(instr):
    """
    Given a header field name in any case, return its properly
    capitalised version.
    
    @param instr: token
    @type instr: string
    @return: HTTP header field-name
    @rtype: string
    """
    return header_name_map.get(instr.lower(), instr.capitalize())

def new_field(name, error_handler=None, **keywords):  #TODO: make into a factory to manage error handler and registration state?
    """
    Return an appropriate FieldValue instance for the given
    (case-insensitive) field-name.
    
    @param name: field-name
    @type name: string
    @param error_handler: handler for header parsing errors
    @type error_handler: L{ErrorHandler} instance
    @param keywords: Extra options for the field
    @return: empty instance
    @rtype: L{FieldValue} 
    """
    field = field_map.get(get_field_name(name), None)
    if field is not None:
        return field(error_handler=error_handler, **keywords)
    else:
        from .field_types import UnknownHeader
        return UnknownHeader(error_handler=error_handler, **keywords)

class FieldValueType(type):
    """
    Type for FieldValues that populates field_map and header_name_map, to keep track
    of field names and their mapping to FieldValue-derived classes.
    """
    def __new__(mcs, name, bases, dict_):
        cls = super(FieldValueType, mcs).__new__(mcs, name, bases, dict_)
        if dict_.has_key('field_name'):
            field_map[dict_['field_name']] = cls
            header_name_map[dict_['field_name'].lower()] = dict_['field_name']
        if dict_.has_key('_parse'):
            cls._parse = classmethod(dict_['_parse'])
        if dict_.has_key('_asString'):
            cls._asString = classmethod(dict_['_asString'])
        return cls
        