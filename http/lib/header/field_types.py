"""
http.header.field_types - HTTP Header Field Data Structures 

This module defines a number of classes which can be used to model HTTP 
header field-values as data structures. Specific headers are mapped to these
structures in the fields module.
"""

__license__ = """
Copyright (c) 1998-2006 Mark Nottingham <mnot@pobox.com>

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

import time, calendar, re, urlparse, sets
from email.Utils import parsedate
from . import registry, error

# Regex for useful BNF rules
TOKEN = r'(?:[^\(\)<>@,;:\\"/\[\]\?={} \t]+?)'
QUOTED_STRING = r'(?:"(?:\\"|[^"])*")'
PARAMETER = r'(?:%(TOKEN)s(?:=(?:%(TOKEN)s|%(QUOTED_STRING)s))?)' % locals()
STRPARAM = r'(?:\S+(?:\s*;\s*%(PARAMETER)s)*)' % locals()
PRODUCT = r'(?:%(TOKEN)s(?:/%(TOKEN)s)?)' % locals()
COMMENT = r'(?:\((?:[^\(\)]|\\\(|\\\))*\))' # does not handle nesting
HTTP_DATE = r'(?:\w{3}, \d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2} GMT|\w{6,9}, \d{2}\-\w{3}\-\d{2} \d{2}:\d{2}:\d{2} GMT|\w{3} \w{3} [\d ]\d \d{2}:\d{2}:\d{2} \d{4})'
ETAG = r'(?:(?:W/)?%(QUOTED_STRING)s|\*)' % locals()
URI = r'(?:\S+)'  # yes, this is cheating
WARNING = r'(?:\d{3} %(TOKEN)s %(QUOTED_STRING)s (?:"%(HTTP_DATE)s")?)' % locals()
BYTERANGE = r'(?:\d*\-\d*)'
COMMA = r'(?:\s*(?:,\s*)+)'


class FieldValueProperty(object):
    """Property representing a FieldValue as a data structure."""
    def __get__(self, obj, objtype=None):
        try:
            if obj._value == obj._default_value:
                if obj._string != "":
                    obj._value = obj._parse(obj._string.strip())
                    obj._string = ""
        except:
            obj.error_handler.handle_error(obj)
        return getattr(obj, "_value", obj._default_value)
    def __set__(self, obj, value):
        obj._value = value
        obj._string = ""
    def __delete__(self, obj):
        obj._string, obj._value = "", obj._default_value

class FieldStringProperty(object):
    """Property representing a FieldValue as a string."""
    def __get__(self, obj, objtype=None):
        if obj._string == "":
            if obj._value != obj._default_value:
                obj._string = obj._asString(obj._value)
                obj._value = obj._default_value
                if __debug__ and obj._string != "" \
                  and not re.match(r"%s$" % obj._line_match, obj._string):
                    try:
                        raise ValueError, "%s is not a valid %s" % (obj._string, obj.__class__)
                    except ValueError:
                        obj.error_handler.handle_error(obj)
            else:
                obj._string = ""
        return obj._string
    def __set__(self, obj, instr):
        instr = instr.strip()
        obj._string = instr
        obj._value = obj._default_value
        if __debug__ and instr != "" \
          and not re.match(r"%s$" % obj._line_match, instr):
            try:
                raise ValueError, "%s is not a valid %s" % (instr, obj.__class__)
            except ValueError:
                obj.error_handler.handle_error(obj)
    def __delete__(self, obj):
        obj._string, obj._value = "", obj._default_value

class FieldValue(object):
    """
    Base class for HTTP Header field-values.
    
    @ivar string: the header field-value as a string.
    @ivar value: the header field-value as a header-specific data structure
    @ivar error_handler: Handler for parsing errors
    @type error_handler: L{error.ErrorHandler} instance
    @cvar _match: a regex that will match one instance of the header value
          (e.g., between commas)
    @type _match: string
    @ivar _line_match: a regex that will match one or more header values
    @type _line_match: string
    @cvar _single_value: whether there can be more than one value (comma-separated)
    @type _single_value: Boolean
    @cvar _default_value: the value for an empty header instance
    """
    __metaclass__ = registry.FieldValueType
    _match = None
    _single_value = True
    _default_value = None
    string = FieldStringProperty()
    value = FieldValueProperty()
    def __init__(self, error_handler=None, **keywords):
        self._string = ""
        self._value = self._default_value
        if self._single_value or isinstance(self, UnfoldableFieldValue):
            self._line_match = self._match
        else:
            self._line_match = r'(?:(?:^\s*|%s)(?:%s|\s*$))+' % (COMMA, self._match)
        self.error_handler = error_handler or error.DefaultErrorHandler()
        [setattr(self, a[0], a[1]) for a in keywords.items()]

class UnfoldableFieldValue(FieldValue):
    """
    A FieldValue that can't or shouldn't have multiple instances 
    folded into one comma-separated header (usually due to syntactic
    ambiguity.) .value must be a list.
    """
    pass

###############################################################################


class UnknownHeader(UnfoldableFieldValue):
    """
    An unknown header field. 

    @type string: 'a b, "c,", d'
    @type value: ["a b", "c,", "d"]
    """
    _match = r".+"
#    _single_value = True # FIXME: special case?
    _default_value = []
    def _parse(cls, instr):
        return [instr]
    def _asString(cls, data):
        return ", ".join(data)

class HttpToken(FieldValue):
    """
    HTTP Token (any CHARs except CTRLs and separators).

    @type string: 'a b'
    @type value: "a b"
    @cvar normalize: normalization function (static)
    """
    _match = TOKEN
    _default_value = None
    normalize = staticmethod(lambda a:a) #IGNORE:E0601
    def _parse(cls, instr):
        return cls.normalize(instr)
    def _asString(cls, data):
        return cls.normalize(data)

class HttpTokenList(FieldValue):
    """
    Group of HTTP Tokens (any CHARs except CTRLs and separators).

    @type string: 'a b, c'
    @type value: ["a b", "c"]
    @cvar normalize: normalization function (static)
    """
    _match = TOKEN
    _single_value = False
    _default_value = []
    normalize = staticmethod(lambda a:a) #IGNORE:E0601
    def _parse(cls, instr):
        return map(cls.normalize, _splitstring(instr, cls._match, COMMA))
    def _asString(cls, data):
        return ", ".join(map(cls.normalize, data))

class Token(FieldValue):
    """
    Token (any CHARs except whitespace).

    @type string: 'ab, c'
    @type value: ["ab", "c"]
    """
    _match = r"\S+"
    _default_value = None
    def _parse(cls, instr):
        return str(instr)
    def _asString(cls, data):
        return str(data)

class QuotedStr(FieldValue):
    """
    Quoted String (<"> any CHARs <">).

    @type string: '"abc"'
    @type value: "abc"
    """
    _match = QUOTED_STRING
    _default_value = None
    def _parse(cls, instr):
        return _unquotestring(instr)
    def _asString(cls, data):
        return _quotestring(data, force=True)

class Int(FieldValue):
    """
    Unsigned Integer.

    @type string: '15'
    @type value: 15
    """
    _match = "\d+"
    _default_value = None
    def _parse(cls, instr):
        return int(instr)
    def _asString(cls, data):
        return str(data)

class ProductComment(FieldValue):
    """
    Product or comment string.
    
    @type string: 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-us) AppleWebKit/412.6.2'
    @type value: ['Mozilla/5.0', '(Macintosh; U; PPC Mac OS X; en-us)', 'AppleWebKit/412.6.2']
    """
    _match = r"%s|%s(?:\s+(?:%s|%s))*" % \
      (PRODUCT, COMMENT, PRODUCT, COMMENT)
    _default_value = []
    def _parse(cls, instr):
        return _splitstring(instr, r'(?:%s|%s)' % \
          (PRODUCT, COMMENT), "\s+")
    def _asString(cls, data):
        return " ".join(data)

class FieldName(Token):
    """
    HTTP header field-name (normalized to canonical capitalization).

    @type string: 'Cache-Control'
    @type value: "Cache-Control"
    """
    _match = TOKEN
    _default_value = None
    def _parse(cls, instr):
        return registry.get_field_name(instr)
    def _asString(cls, data):
        return registry.get_field_name(data)

class FieldNameList(FieldValue):
    """
    Group of HTTP header field-names (normalized).
    
    @type string: 'Cache-Control, Connection'
    @type value: ["Cache-Control", "Connection"]
    """
    _match = TOKEN
    _single_value = False
    _default_value = []
    def _parse(cls, instr):
        return map(registry.get_field_name, _splitstring(instr, cls._match, COMMA))        
    def _asString(cls, data):
        return ", ".join(map(registry.get_field_name, data))
            
class HttpDate(FieldValue):
    """
    HTTP Date. None if the date is invalid.
    
    @type string: string
    @type value: seconds since epoch
    """
    _match = HTTP_DATE  
    _default_value = None
    def _parse(cls, instr):
        return _parse_http_date(instr)
    def _asString(cls, data):
        return _http_date_as_string(data)

class Uri(FieldValue):
    """
    URI (absolute or relative).

    @type string: 'http://www.example.com/widget'
    @type value: ["http", "www.example.com", "widget", "", ""]
    """
    _match = URI
    _default_value = None
    def _parse(cls, instr):
        return list(urlparse.urlsplit(instr))
    def _asString(cls, data):
        return urlparse.urlunsplit(tuple(data))


class EntityTag(FieldValue): 
    """
    Entity tag.

    @type string: 'W/"abc"'
    @type value: ("abc", True)
    """
    _match = ETAG
    _default_value = None
    def _parse(cls, instr):
        if instr[:2] == 'W/':
            return (_unquotestring(instr[2:]), True)
        else:
            return (_unquotestring(instr), False)
    def _asString(cls, data):
        weak_str = ''
        if data[1] is True:
            weak_str = "W/"
        return "%s%s" % (weak_str, _quotestring(data[0], force=True)) 

class EntityTagDict(FieldValue):
    """
    Group of entity tags.

    @type string: '"abc", W/"def", "ghi"'
    @type value: {"abc": False, "def": True, "ghi": False}
    """
    _match = ETAG
    _single_value = False
    _default_value = {}
    def _parse(cls, instr):
        out = {}
        for etag in _splitstring(instr, cls._match, COMMA):
            if etag[:2] == 'W/':
                out[_unquotestring(etag[2:])] = True
            else:
                out[_unquotestring(etag)] = False
        return out
    def _asString(cls, data):
        out = []
        for etag, weak in data.items():
            if weak:
                weak_str = 'W/'
            else:
                weak_str = ''
            out.append("%s%s" % (weak_str, _quotestring(etag, force=True)))
        return ", ".join(out)

class ParamDict(FieldValue):
    """
    Group of parameters.

    @type string: 'abc=def, ghi, jkl="mn,o"'
    @type value: {"abc": "def", "ghi": None, "jkl": "mn,o"}
    @cvar force_quote: parameter names whose value is always to be quoted
    @type force_quote: list of strings
    """
    _match = PARAMETER
    _single_value = False
    _default_value = {}
    force_quote = []
    def _parse(cls, instr):
        out = {}
        for param in _splitstring(instr, cls._match, COMMA):
            try:
                attr, value = param.split("=", 1)
                value = _unquotestring(value)
            except ValueError:
                attr = param
                value = None
            out[attr.lower()] = value
        return out
    def _asString(cls, data):
        out = []
        for attr, value in data.items():
            if value is None:
                out.append(attr)
            else:
                force = attr in cls.force_quote or \
                  ";" in value or \
                  "," in value
                out.append("%s=%s" % (attr, _quotestring(value, force=force)))
        return ", ".join(out)

class StrParam(FieldValue):
    """
    Token with an arbitrary number of parameters. Parameter names
    are normalised to lowercase.

    @type string: 'abc; DEF=ghi; jkl; mno="p,q"'
    @type value: ["abc", {"def": "ghi", "jkl": None, "mno": "p,q"}]
    @cvar normalize: normalization function for the token (static)
    @cvar param_sort: static function to sort parameters upon output
    @cvar force_quote: parameter names whose values must be quoted
    @type force_quote: list of strings    
    """
    _match = STRPARAM
    _default_value = [None, {}]
    normalize = staticmethod(lambda a:a) #IGNORE:E0601
    param_sort = staticmethod(lambda a, b:0)
    force_quote = []
    def _parse(cls, instr):
        try:
            s, params = instr.split(";", 1)
        except ValueError:
            s, params = instr, ''
        param_dict = {}
        for param in _splitstring(params, PARAMETER, "\s*;\s*"):
            try:
                a, v = param.split("=", 1)
                param_dict[a.lower()] = _unquotestring(v)
            except ValueError:
                param_dict[param.lower()] = None
        return [cls.normalize(s), param_dict]
    def _asString(cls, data):
        token = data[0] or ""
        params = data[1].items()
        params.sort(cls.param_sort)
        o, param_string = [], ""
        for k, v in params:
            if v == None:
                o.append(k)
            else:
                o.append("%s=%s" % (
                  k, _quotestring(v, force=(k in cls.force_quote))))
        if o != []:
            param_string = '; ' + "; ".join(o)
        return "%s%s" % (cls.normalize(token), param_string)

class StrParamDict(FieldValue):
    """
    Group of tokens with an arbitrary number of parameters.
    Parameter names are normalised to lowercase.
    
    @type string: 'abc; def=ghi; jkl; mno="p,q", rst, uv; wx=yz'
    @type value: {"abc": {"def": "ghi", "jkl": None}, "rst": {}, "uv": {"wx": "yz"}}
    @ivar normalize: normalization function for the token (static)
    @cvar param_sort: static function to sort parameters upon output
    @cvar force_quote: parameter names whose values must be quoted
    @type force_quote: list of strings
    """
    _match = STRPARAM
    _single_value = False
    _default_value = {}
    normalize = staticmethod(lambda a:a) #IGNORE:E0601
    param_sort = staticmethod(lambda a, b:0)
    force_quote = []
    def _parse(cls, instr):
        out = {}
        for strparam in _splitstring(instr, cls._match, COMMA):
            try:
                s, params = strparam.split(";", 1)
            except ValueError:
                s, params = strparam, ''
            param_dict = {}
            for param in _splitstring(params, PARAMETER, "\s*;\s*"):
                if param.strip() == "": continue
                try:
                    a, v = param.split("=", 1)
                    param_dict[a.lower()] = v
                except ValueError:
                    param_dict[param.lower()] = None
            out[cls.normalize(s)] = param_dict
        return out       
    def _asString(cls, data):
        out = []
        for s, params in data.items():
            pout = []
            sep = ""
            param_list = params.items()
            param_list.sort(cls.param_sort)
            for k, v in param_list:
                if v is None:
                    pout.append(k)
                else:
                    pout.append("%s=%s" % (k, _quotestring(v)))
            if pout != []:
                sep = "; "
            out.append("%s%s%s" % (cls.normalize(s), sep, "; ".join(pout)))
        return ", ".join(out)

class ChallengeList(FieldValue):
    """
    Group of HTTP Authentication challenges.

    @type string: "Basic realm=Test"
    @type value: [["Basic", {"realm": "Test"}]]
    @cvar force_quote: parameter names whose values must be quoted
    @type force_quote: list of strings
    """
    _match = r"%s\s+(?:%s(?:%s%s)*)?" % (TOKEN, PARAMETER, COMMA, PARAMETER)
    _single_value = False
    _default_value = []
    force_quote = ['domain', 'nonce', 'opaque', 'qop']
    def _parse(cls, instr):
        out = []
        for challenge in _splitstring(instr, cls._match, COMMA):
            try:
                scheme, args = challenge.split(None, 1)
            except ValueError:
                scheme, args = instr, ''
            params = {}
            for param in _splitstring(args, "%s" % PARAMETER, COMMA):
                try:
                    attr, value = param.split("=", 1)
                    params[attr.lower()] = _unquotestring(value)
                except ValueError:
                    params[param.lower()] = None
            out.append([scheme.capitalize(), params])
        return out
    def _asString(cls, data):
        out = []
        for scheme, params in data:
            o = []
            for k, v in params.items():
                if v == None:
                    o.append(k)
                else:
                    o.append("%s=%s" % (
                      k, _quotestring(v, force=(k.lower() in cls.force_quote))))
            out.append("%s %s" % (scheme, ", ".join(o)))
        return ", ".join(out)

class Credentials(FieldValue):
    """
    HTTP Authentication credentials.
    
    @type string: 'Digest username="Mufasa", realm="testrealm@host.com", qop=auth'
    @type value: ["Digest", {"username": "Mufasa", "realm": "testrealm@host.com", "qop": "auth"}]
    @cvar force_quote: parameter names whose values must be quoted 
    @type force_quote: list of strings    
    """
    _match = r"%s\s(?:%s(?:%s%s)*)?" % (TOKEN, PARAMETER, COMMA, PARAMETER)
    _default_value = [None, {}]
    force_quote = ['username', 'uri', 'response']
    def _parse(cls, instr):
        try:
            scheme, args = instr.split(None, 1)
        except ValueError:
            scheme, args = instr, ''
        params = {}
        for param in _splitstring(args, "%s" % PARAMETER, COMMA):
            try:
                attr, value = param.split("=", 1)
                params[attr.lower()] = _unquotestring(value)
            except ValueError:
                params[param.lower()] = None
        return [scheme.capitalize(), params]
    def _asString(cls, data):
        o = []
        for k, v in data[1].items():
            if v == None:
                o.append(k)
            else:
                o.append("%s=%s" % (
                  k, _quotestring(v, force=(k.lower() in cls.force_quote))))
        return "%s %s" % (data[0], ", ".join(o))

class WarningValueList(FieldValue):
    """
    Group of warning values.

    @type string: '199 www.example.com:85 "Something's wrong" "Sat, 04 Jun 1977 00:50:23 GMT"'
    @type value: [{"code": "199", "agent": "www.example.com:85", "text": "Something's wrong", "date": 234233423},]
    """
    _match = WARNING
    _single_value = False
    _default_value = []
    def _parse(cls, instr):
        out = []
        for warning in _splitstring(instr, cls._match, COMMA):
            l = warning.split(None, 3)
            l.reverse()
            code = int(l.pop())
            agent = l.pop()
            text = _unquotestring(l.pop())
            try:
                date = _parse_http_date(l.pop())
            except IndexError:
                date = None
            out.append({'code': code, 'agent': agent, 'text': text, 'date': date})
        return out            
    def _asString(cls, data):
        o = []
        for warn in data:
            try:
                warn_date = " " + _http_date_as_string(warn['date'])
            except KeyError:
                warn_date = ""
            o.append('%s %s %s%s' % (
              warn['code'],
              warn['agent'], 
              _quotestring(warn['text'], force=1), 
              warn_date)
            )
        return ", ".join(o)

class ContentRange(FieldValue):
    """
    Byte-content-range-spec.
    
    @type string: "bytes 0-500/1600"
    @type value: (0, 500, 1600)
    """
    _match = r"%s (?:\d+\-\d+|\*)/(?:\d+|\*)"
    _default_value = (None, None, None)
    def _parse(cls, instr):
        range_type, content_range = instr.split(None)
        if range_type.lower() != 'bytes':
            raise NotImplementedError, "Only 'bytes' byte-range supported"
        byte_range_resp, instance_length = content_range.split('/')
        if byte_range_resp == '*':
            first_byte_pos, last_byte_pos = None, None
        else:
            first_byte_pos, last_byte_pos = [int(i) for i in byte_range_resp.split('-')]
        if instance_length == '*':
            instance_length = None
        return (first_byte_pos, last_byte_pos, instance_length)

    def _asString(cls, data):
        (first_byte_pos, last_byte_pos, instance_length) = data
        if first_byte_pos is None or last_byte_pos is None:
            byte_range_resp = "*"
        else:
            byte_range_resp = "%s-%s" % (first_byte_pos, last_byte_pos)
        if instance_length is None:
            instance_length = '*'
        return "bytes %s/%s" % (byte_range_resp, instance_length)
        
class ByteRangeList(FieldValue):
    """
    List (ordering insignifiant) of byte range specs.
    
    @type string: "500-600, -50, 2500-"
    @type value: Set([(500, 600), (-50, None), (2500, None)])
    """
    _match = BYTERANGE
    _single_value = False
    _default_value = []  
    def _parse(cls, instr):
        out = []
        for byterange in _splitstring(instr, cls._match, COMMA):
            out.append([pos or None for pos in byterange.split('-', 1)])
        return out

    def _asString(cls, data):
        o = []
        for byterange in data:
            o.append('-'.join([pos or '' for pos in byterange]))
        return ', '.join(o)
    
class EntityTagOrHttpDate(FieldValue):
    """
    Either an Entity Tag or a HTTP Date.
        
    @type string: 'W/"12345"'
    @type value: {"type": "etag", "value": "12345", "weak": True}
    """
    _match = r'(?:%s|%s)' % (ETAG, HTTP_DATE) 
    _default_value = {"type": None}
    def _parse(cls, instr):
        if instr[-1] == '"':
            if instr[:3] == 'W/"':
                return {'type': 'etag', 'weak': True, 'value': _unquotestring(instr[2:])}
            elif instr[0] == '"':
                return {'type': 'etag', 'weak': False, 'value': _unquotestring(instr)}
        else:
            return {'type': 'date', 'value': _parse_http_date(instr)}
    def _asString(cls, data):
        if data['type'] == 'etag':
            if data['weak']:
                return "W/%s" % _quotestring(data['value'], force=True)
            else:
                return _quotestring(data['value'], force=True)
        else:
            return _http_date_as_string(data['value'])
    
class ViaList(FieldValue):
    """
    List of information specific to the intermediaries a message
    passes through.

    @type string: 'HTTP/1.0 fred, 1.1 nowhere.com (Apache/1.1)'
    @type value: [['HTTP/1.0', 'fred', None], ['HTTP/1.1'], 'nowhere.com', 'Apache/1.1']
    """
    _match = r'(?:%s/)?%s\s+[^,\s]+(?:\s+%s)?' % (TOKEN, TOKEN, COMMENT)
    _single_value = False
    _default_value = []
    def _parse(cls, instr):
        out = []
        for via in _splitstring(instr, cls._match, COMMA):
            received_protocol, rest = via.split(None, 1)
            try:
                received_by, comment = rest.split(None, 1)
            except ValueError:
                received_by, comment = rest, None
            out.append([received_protocol, received_by, comment])
    def _asString(cls, data):
        o = []
        for via in data:
            received_protocol, received_by, comment = via
            if comment is not None:
                comment = " " + comment
            o.append("%s %s%s" % (received_protocol.upper(), received_by, comment or ""))
        return ", ".join(o)

####################################################################

def _quotestring(instr, force=False):
    """
    Quote a string; does NOT quote control characters. If force
    is true, instr will be quoted whether it needs to or not.
    
    @param instr: string to be quoted
    @type instr: string
    @param force: whether or not to always quote, regardless of need
    @type force: boolean
    @return: quoted string
    @rtype: string        
    """
    instr = str(instr)
    if not force and not re.search(r'[",\\;]', instr):
        return instr
    if instr == '*':
        return instr
    instr = re.sub(r'\\', r'\\\\', instr)
    return '"%s"' % (re.sub(r'"', r'\\"', instr))

def _unquotestring(instr):
    """
    Unquote a string; does NOT unquote control characters. 
    
    @param instr: string to be unquoted
    @type instr: string
    @return: unquoted string
    @rtype: string
    """
    instr = str(instr).strip()
    if not instr or instr == '*':
        return instr
    if instr[0] == instr[-1] == '"':
        instr = instr[1:-1]
        instr = re.sub(r'\\(.)', r'\1', instr)
    return instr

def _splitstring(instr, item, split):
    """
    Split instr as a list of items separated by splits.
    
    @param instr: string to be split
    @param item: regex for item to be split out
    @param split: regex for splitter
    @return: list of strings
    """
    if not instr: return []
    return [ h.strip() for h in re.findall(r'%s(?=%s|\s*$)' % (item, split), instr)]
          
def _parse_http_date(instr):
    """
    @param instr: HTTP date string
    @type instr: string
    @return: seconds since the epoch
    @rtype: int
    """
    date_tuple = parsedate(instr)
    # http://sourceforge.net/tracker/index.php?func=detail&aid=1194222&group_id=5470&atid=105470
    if date_tuple[0] < 100:
        if date_tuple[0] > 68:
            date_tuple = (date_tuple[0]+1900,)+date_tuple[1:]
        else:
            date_tuple = (date_tuple[0]+2000,)+date_tuple[1:]
    return calendar.timegm(date_tuple)
    
def _http_date_as_string(data):
    """
    @param data: seconds since the epoch
    @type data: int
    @return: HTTP date string
    @rtype: string
    """
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(data))