#!/usr/bin/env python2.5

import unittest
from copy import copy
from ..lib.header import field_types, error

error.DefaultErrorHandler = error.RaiseErrorHandler
# TODO: negative testing
        
class HeaderTypeTestCase:
    header_type = field_types.UnknownHeader
    default_string = ""
    canonical_pairs = []
    canonical_value_pairs = []
    
    def setUp(self):
        self.header = self.header_type()
        
    def testFromString(self):
        for s, v in self.canonical_pairs + self.canonical_value_pairs:
            self.header.string = s
            self.assertEqual(self.header.value, v, "(%s, %s)" % (self.header.value, v))

    def testFromValue(self):
        for s, v in self.canonical_pairs:
            self.header.value = v
            self.assertEqual(self.header.string, s, "(%s, %s)" % (self.header.string, s))

    def testStringValueString(self):
        for s, v in self.canonical_pairs:
            self.header.string = s
            self.header.value = v
            self.assertEqual(self.header.string, s, "(%s, %s)" % (self.header.string, s))

    def testValueStringValue(self):
        for s, v in self.canonical_pairs + self.canonical_value_pairs:
            self.header.value = v
            self.header.string = s
            self.assertEqual(self.header.value, v, "(%s, %s)" % (self.header.value, v))
            
    def testStringDeletion(self):
        for s, v in self.canonical_pairs:
            self.header.string = s
            del self.header.string
            self.assert_(self.header.string == self.default_string, "(%s, %s)" % (self.header.string, self.default_string))
            if self.default_string != s:
                self.assert_(self.header.value != v, "(%s, %s)" % (self.header.value, v))
                    
    def testValueDeletion(self):
        for s, v in self.canonical_pairs:
            self.header.value = v
            del self.header.value
            self.assert_(self.header.value == self.header._default_value, "(%s, %s)" % (self.header.value, self.header._default_value))
            if self.header._default_value != v:
                self.assert_(self.header.string != s, "(%s, %s)" % (self.header.string, s))

    def testIdempotentDeleteString(self):
        self.header.string = self.canonical_pairs[-1][0]
        del self.header.string
        tmp = copy(self.header.string)
        del self.header.string
        self.assertEqual(tmp, self.header.string, "(%s, %s)" % (tmp, self.header.string))

    def testIdempotentDeleteValue(self):
        self.header.value = self.canonical_pairs[-1][1]
        del self.header.value
        tmp = copy(self.header.value)
        del self.header.value
        self.assertEqual(tmp, self.header.value, "(%s, %s)" % (tmp, self.header.value))

class TestUnknownHeaderType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.UnknownHeader
    canonical_pairs = [
        ("", []),
        (",", [","]),
        ("1", ["1"]), 
        ("a", ["a"]), 
        ("A", ["A"]),
        ("abc", ["abc"]),
        ("Ab Cd", ["Ab Cd"]),
        ("ab, cd", ["ab, cd"]),
        ('ab, cd="f,g"', ['ab, cd="f,g"']),
        ("ab,cd", ["ab,cd"]),
    ]
    canonical_value_pairs = [
        (" ", []),
    ]

class TestHttpTokenType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.HttpToken
    canonical_pairs = [
        ("", None),
        ("a", "a"),
        ("ab", "ab"),
        ("a123b456", "a123b456"),
    ]

class TestHttpTokenListType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.HttpTokenList
    canonical_pairs = [
        ("", []),
        ("a", ["a"]),
        ("a, b", ["a", "b"]),
        ("abc, DEF", ["abc", "DEF"]),
        ("ab, de", ["ab", "de"]),
    ]
    canonical_value_pairs = [
        (" ", []),
        ("a,b", ["a", "b"]),
        (",", []), # TODO: repeat this test style elsewhere
        ("a,,", ['a']),  
        ("a,,b", ['a', 'b']),
    ]

class TestTokenType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.Token
    canonical_pairs = [
        ("", None),
        ("a", "a"),
        ("ab", "ab"),
        ("a123b456", "a123b456"),
        ("www.example.com:80", "www.example.com:80"),
        ("bob!jane-john@example.com", "bob!jane-john@example.com"),
        ("1.0", "1.0"), 
    ]

class TestQuotedStrType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.QuotedStr
    canonical_pairs = [
        ("", None),
        ('""', ""),
        ('"a"', "a"),
        ('"a,b"', "a,b"),
        (r'"a,b\"c\""', 'a,b"c"'),
    ]
    
class TestIntHeaderType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.Int
    canonical_pairs = [
        ("", None),
        ("0", 0),
        ("1", 1), 
        ("2134234234234", 2134234234234),
    ]
    canonical_value_pairs = [
        (" 1 ", 1),
    ]
        
class TestFieldNameType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.FieldName
    canonical_pairs = [
        ("", None),
        ("Foo", "Foo"),
        ("Cache-Control", "Cache-Control"),
    ]
    canonical_value_pairs = [
        ("foo", "Foo"),
        ("cachE-controL", "Cache-Control"),
    ]

class TestFieldNameListType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.FieldNameList
    canonical_pairs = [
        ("", []),
        ("Foo", ["Foo"]),
        ("Foo, Cache-Control, Host", ["Foo", "Cache-Control", "Host"])
    ]
    canonical_value_pairs = [
        ("foo, bar, host", ["Foo", "Bar", "Host"]),
        (",", []),
        ("foo,,", ["Foo"]),
        ("foo,,bar", ["Foo", "Bar"]),
    ]

class TestHttpDateType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.HttpDate
    canonical_pairs = [
        ("", None),
        ("Sun, 06 Nov 1994 08:49:37 GMT", 784111777),
    ]
    canonical_value_pairs = [
        ("Sunday, 06-Nov-94 08:49:37 GMT", 784111777),
        ("Sun Nov  6 08:49:37 1994", 784111777),
    ]

class TestUriType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.Uri
    canonical_pairs = [
        ('http://www.example.com/foo/bar?baz=bat#bam',
          ['http', 'www.example.com', '/foo/bar', 'baz=bat', 'bam']),
    ]

class TestEntityTagType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.EntityTag
    canonical_pairs = [
        ('', None),
        ('""', ("", False)),
        ('"abc"', ('abc', False)),
        (r'W/"abc"', ('abc', True)),
        (r'W/""', ("", True)),
    ]

class TestEntityTagDictType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.EntityTagDict
    canonical_pairs = [
        ("", {}),
        ('"123,456"', {"123,456": False}),
        ('*', {"*": False}),
    ]
    canonical_value_pairs = [
        ('"abc", "def"', {    
                            "abc": False,
                            "def": False,
                         }),
        (r'W/"ghi", "jkl"', {
                            "ghi": True,
                            "jkl": False,
                          }),
    ]

class TestParamDictType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.ParamDict
    canonical_pairs = [
        ("", {}),
        ("abc=def", {'abc': 'def'}),
        ("abc", {"abc":None}),
        ("$foo=bar", {"$foo": "bar"}),
    ]
    canonical_value_pairs = [
        ("abc=def, ghi, jkl=mno", {"abc": "def", "ghi": None, "jkl": "mno"}),
        ('abc="def,ghi", jkl=mno', {"abc": "def,ghi", "jkl": "mno"}),
#        ('abc="def\"ghi", jkl=mno', {"abc": 'def"ghi', "jkl": "mno"}),
    ]

class TestStrParamType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.StrParam
    canonical_pairs = [
        ("", [None, {}]),
        ("text/html", ["text/html", {}]),
        ("text/html; charset=utf-8", ["text/html", {"charset": "utf-8"}]),
    ]
    canonical_value_pairs = [
        ("text/html;CHarSET=utf-8 ;q=1.0", ["text/html", {"charset": "utf-8", "q": "1.0"}]),
    ]

class TestStrParamDictType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.StrParamDict
    canonical_pairs = [
        ("", {}),
        ("text/html", {"text/html": {}}),
        ("text/html; charset=utf-8", {"text/html": {"charset": "utf-8"}}),
        ("*", {"*": {}}),
    ]
    canonical_value_pairs = [
        ("text/html;CHarSET=utf-8 ;q=1.0", {"text/html": {"charset": "utf-8", "q": "1.0"}}),
        ("text/html, text/plain", {"text/html": {}, "text/plain": {}}),
        ("text/html; q=1.0, text/plain; q=0.5", {"text/html": {"q": "1.0"}, "text/plain": {"q": "0.5"}}),
    ]

class TestChallengeListType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.ChallengeList
    canonical_pairs = [
        ("", []),
        ("Basic realm=Test", [["Basic", {"realm": "Test"}]]),
        ("Basic realm=Test, Basic realm=Other", 
          [["Basic", {"realm": "Test"}], ["Basic", {"realm": "Other"}]]),
    ]
    canonical_value_pairs = [
        ('Digest realm="testrealm@host.com", qop="auth,auth-int", nonce="dcd9", opaque="5cc"', 
         [["Digest", {"realm": "testrealm@host.com", "qop": "auth,auth-int", "nonce": "dcd9", "opaque": "5cc"}]]),
        ('digesT RealM=foo', [['Digest', {"realm": "foo"}]]),
    ]
    
class TestCredentialsType(HeaderTypeTestCase, unittest.TestCase):
    header_type = field_types.Credentials
    canonical_pairs = [
        ("", [None, {}]),
        ("Basic abcdef", ["Basic", {"abcdef": None}]),
    ]
    canonical_value_pairs = [
        ('Digest username="Mufasa", realm="testrealm@host.com", qop=auth',
         ["Digest", {"username": "Mufasa", "realm": "testrealm@host.com", "qop": "auth"}]
        ),
    ]

#TODO: class TestProductCommentType(HeaderTypeTestCase, unittest.TestCase):
#    header_type = field_types.ProductComment

#TODO: class TestWarningListType(HeaderTypeTestCase, unittest.TestCase):
#    header_type = field_types.WarningList

#TODO: class TestByteRangeListType(headerTypeTestCase, unittest.TestCase):
#    header_type = field_types.ByteRangeList

#TODO: class TestContentRangeType(headerTypeTestCase, unittest.TestCase):
#    header_type = field_types.ContentRange

#TODO: class TestEntityTagOrHttpDate(headerTypeTestCase, unittest.TestCase):
#    header_type = field_types.EntityTagOrHttpDate

#TODO: class TestViaList(headerTypeTestCase, unittest.TestCase):
#    header_type = field_types.ViaList

#TODO: class TestNewField(unittest.TestCase):

#TODO: class TestDictCollection(unittest.TestCase):

#TODO: class TestRealWorldHeaders(unittest.TestCase):


if __name__ == '__main__':
    import header.fields # populates the registry
    unittest.main()