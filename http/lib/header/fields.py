"""
http.header.fields - HTTP Header Fields 
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

# TODO: headers from TCN (2295)
# TODO: headers from DAV (2518) - If, Lock-Token, Status-URI
# TODO: PICS-Label
# TODO: Cookie, Set-Cookie, Cookie2

import string #IGNORE:W0402
from . import field_types as ft
from .utility import sortQValLast

class AIMHeader(ft.StrParamDict):
    """
    The A-IM request-header field is similar to Accept, but 
    restricts the instance-manipulations (section 10.1) that 
    are acceptable in the response.
    
    A-IM = "A-IM" ":" #( instance-manipulation
                          [ ";" "q" "=" qvalue ] )
    """
    field_name = "A-IM"
    normalize = staticmethod(string.lower)    
    
class AcceptHeader(ft.StrParamDict):
    """
    The Accept request-header field can be used to specify 
    certain media types which are acceptable for the response.
    
    Accept = "Accept" ":" #( media-range [ accept-params ] ) 
    """
    field_name = "Accept"
    param_sort = staticmethod(sortQValLast)
    normalize = staticmethod(string.lower)

class AcceptCharsetHeader(ft.StrParamDict):
    """
    The Accept-Charset request-header field can be used to 
    indicate what character sets are acceptable for the response.

    Accept-Charset = "Accept-Charset" ":" 
                     1#( ( charset | "*" )[ ";" "q" "=" qvalue ] )
    """
    field_name = "Accept-Charset"
    param_sort = staticmethod(sortQValLast)

class AcceptEncodingHeader(ft.StrParamDict):
    """
    The Accept-Encoding request-header field restricts the 
    content-codings that are acceptable in the response.

    Accept-Encoding = "Accept-Encoding" ":" 
                      1#( codings [ ";" "q" "=" qvalue ] )    
    """
    field_name = "Accept-Encoding"

class AcceptLanguageHeader(ft.StrParamDict):
    """
    The Accept-Language request-header field restricts the set 
    of natural languages that are preferred as a response to 
    the request.

    Accept-Language = "Accept-Language" ":" 
                      1#( language-range [ ";" "q" "=" qvalue ] )    
    """
    field_name = "Accept-Language"

class AcceptRangesHeader(ft.HttpTokenList):
    """
    The Accept-Ranges response-header field allows the server 
    to indicate its acceptance of range requests for a resource.    
    
    Accept-Ranges = "Accept-Ranges" ":" acceptable-ranges
    """
    field_name = "Accept-Ranges"
        
class AgeHeader(ft.Int):
    """
    The Age response-header field conveys the sender's estimate 
    of the amount of time since the response (or its 
    revalidation) was generated at the origin server.
    
    Age = "Age" ":" age-value
    """
    field_name = "Age"

class AllowHeader(ft.HttpTokenList):
    """
    The Allow entity-header field lists the set of methods 
    supported by the resource identified by the Request-URI.   

    Allow = "Allow" ":" #Method
    """
    field_name = "Allow"
    normalize = staticmethod(string.upper)

class AuthenticationInfoHeader(ft.ParamDict):
    """
    The Authentication-Info header is used by the server to 
    communicate some information regarding the successful 
    authentication in the response.
    """
    field_name = "Authentication-Info"

class AuthorizationHeader(ft.Credentials):
    """
    A user agent that wishes to authenticate itself with a 
    server--usually, but not necessarily, after receiving a 401 
    response--does so by including an Authorization request-header 
    field with the request. The Authorization field value consists 
    of credentials containing the authentication information of the 
    user agent for the realm of the resource being requested.
    
    Authorization = "Authorization" ":" credentials
    """
    field_name = "Authorization"

class CacheControlHeader(ft.ParamDict):
    """
    The Cache-Control general-header field is used to specify
    directives that MUST be obeyed by all caching mechanisms 
    along the request/response chain.

    Cache-Control = "Cache-Control" ":" 1#cache-directive
    """    
    field_name = "Cache-Control"

class ConnectionHeader(ft.HttpTokenList):
    """
    The Connection general-header field allows the sender to 
    specify options that are desired for that particular 
    connection and MUST NOT be communicated by proxies over 
    further connections.

    Connection = "Connection" ":" 1#(connection-token)
    """
    field_name = "Connection"

class ContentBaseHeader(ft.Uri):
    """
    The Content-Base entity-header field may be used to 
    specify the base URI for resolving relative URLs within
    the entity.

    Content-Base = "Content-Base" ":" absoluteURI
    """
    field_name = "Content-Base"
        
class ContentDispositionHeader(ft.StrParam):
    """
    The Content-Disposition response-header field has been 
    proposed as a means for the origin server to suggest a 
    default filename if the user requests that the content 
    is saved to a file. This usage is derived from the 
    definition of Content-Disposition in RFC 1806.

    content-disposition = "Content-Disposition" ":"
                  disposition-type *( ";" disposition-parm )
    """
    field_name = "Content-Disposition"
    
class ContentEncodingHeader(ft.HttpTokenList):
    """
    The Content-Encoding entity-header field indicates what 
    additional content codings have been applied to the 
    entity-body, and thus what decoding mechanisms must be 
    applied in order to obtain the media-type referenced by 
    the Content-Type header field.

    Content-Encoding = "Content-Encoding" ":" 1#content-coding
    """
    field_name = "Content-Encoding"
    
class ContentLanguageHeader(ft.HttpTokenList):
    """
    The Content-Language entity-header field describes the 
    natural language(s) of the intended audience for the 
    enclosed entity.

    Content-Language = "Content-Language" ":" 1#language-tag
    """
    field_name = "Content-Language"
    
class ContentLengthHeader(ft.Int):
    """
    The Content-Length entity-header field indicates the 
    size of the entity-body, in decimal number of OCTETs, 
    sent to the recipient or, in the case of the HEAD method, 
    the size of the entity-body that would have been sent 
    had the request been a GET.

    Content-Length = "Content-Length" ":" 1*DIGIT 
    """
    field_name = "Content-Length"
    
class ContentLocationHeader(ft.Uri):
    """
    The Content-Location entity-header field MAY be used to 
    supply the resource location for the entity enclosed in 
    the message when that entity is accessible from a 
    location separate from the requested resource's URI.

    Content-Location = "Content-Location" ":" 
                         ( absoluteURI | relativeURI )
    """
    field_name = "Content-Location"
    
class ContentMD5Header(ft.Token):
    """
    The Content-MD5 entity-header field, as defined in RFC 
    1864, is an MD5 digest of the entity-body for the purpose 
    of providing an end-to-end message integrity check (MIC) 
    of the entity-body.
    
    Content-MD5 = "Content-MD5" ":" md5-digest
    """
    field_name = "Content-MD5"

class ContentRangeHeader(ft.ContentRange):
    """
    The Content-Range entity-header is sent with a partial 
    entity-body to specify where in the full entity-body the 
    partial body should be applied.
    
    Content-Range = "Content-Range" ":" content-range-spec
    """
    field_name = "Content-Range"

class ContentTypeHeader(ft.StrParam):
    """
    The Content-Type entity-header field indicates the media 
    type of the entity-body sent to the recipient or, in the 
    case of the HEAD method, the media type that would have been 
    sent had the request been a GET.

    Content-Type = "Content-Type" ":" media-type
    """
    field_name = "Content-Type"
    
class ContentVersionHeader(ft.QuotedStr):
    """
    The Content-Version entity-header field defines the 
    version tag associated with a rendition of an evolving 
    entity. Together with the Derived-From field, it 
    allows a group of people to work simultaneously on the 
    creation of a work as an iterative process. The field 
    should be used to allow evolution of a particular work 
    along a single path rather than derived works or
    renditions in different representations.

    Content-Version = "Content-Version" ":" quoted-string    
    """
    field_name = "Content-Version"
    
class DateHeader(ft.HttpDate):
    """
    The Date general-header field represents the date and time 
    at which the message was originated.

    Date = "Date" ":" HTTP-date
    """
    field_name = "Date"

class DAVHeader(ft.HttpTokenList):
    """
    This general-header appearing in the response indicates 
    that the resource supports the DAV schema and protocol 
    as specified.
    
    DAV             = "DAV" ":" #( compliance-code )
    compliance-code = ( "1" | "2" | "bis" | extend )
    extend          = Coded-URL | token    
    """
    field_name = "DAV"
    normalize = staticmethod(string.lower)

class DeltaBaseHeader(ft.EntityTag):
    """
    The Delta-Base entity-header field is used in a 
    delta-encoded response to specify the entity tag 
    of the base instance.
    
    Delta-Base = "Delta-Base" ":" entity-tag
    """
    field_name = "Delta-Base"

class DepthHeader(ft.HttpToken):
    """
    The Depth request header is used with methods executed on 
    resources which could potentially have internal members to 
    indicate whether the method is to be applied only to the 
    resource ("Depth: 0"), to the resource and its immediate 
    children, ("Depth: 1"), or the resource and all its progeny 
    ("Depth: infinity").
    
    Depth = "Depth" ":" ("0" | "1" | "infinity")
    """
    field_name = "Depth"

class DestinationHeader(ft.Uri):
    """
    The Destination request header specifies the URI which 
    identifies a destination resource for methods such as COPY 
    and MOVE, which take two URIs as parameters.
    
    Destination = "Destination" ":" ( absoluteURI )
    """
    field_name = "Destination"
    
class ETagHeader(ft.EntityTag):
    """
    The ETag response-header field provides the current value 
    of the entity tag for the requested variant.

    ETag = "ETag" ":" entity-tag
    """
    field_name = "ETag"
    
class ExpectHeader(ft.HttpToken):
    """
    The Expect request-header field is used to indicate that 
    particular server behaviors are required by the client.

    Expect = "Expect" ":" 1#expectation
    """
    field_name = "Expect"
    
class ExpiresHeader(ft.HttpDate):
    """
    The Expires entity-header field gives the date/time after 
    which the response is considered stale.
    
    Expires = "Expires" ":" HTTP-date
    """
    field_name = "Expires"
    
class FromHeader(ft.Token):
    """
    The From request-header field, if given, SHOULD contain 
    an Internet e-mail address for the human user who controls 
    the requesting user agent.

    From = "From" ":" mailbox
    """
    field_name = "From"
    
class HostHeader(ft.Token):
    """
    The Host request-header field specifies the Internet host 
    and port number of the resource being requested, as 
    obtained from the original URI given by the user or 
    referring resource.

    Host = "Host" ":" host [ ":" port ]
    """
    field_name = "Host"
    
class IfMatchHeader(ft.EntityTagDict):
    """
    The If-Match request-header field is used with a method 
    to make it conditional. A client that has one or more 
    entities previously obtained from the resource can verify 
    that one of those entities is current by including a list 
    of their associated entity tags in the If-Match header 
    field.
    
    If-Match = "If-Match" ":" ( "*" | 1#entity-tag )
    """
    field_name = "If-Match"
    
class IfModifiedSinceHeader(ft.HttpDate):
    """
    The If-Modified-Since request-header field is used with 
    a method to make it conditional: if the requested variant 
    has not been modified since the time specified in this 
    field, an entity will not be returned from the server; 
    instead, a 304 (not modified) response will be returned 
    without any message-body.

    If-Modified-Since = "If-Modified-Since" ":" HTTP-date 
    """
    field_name = "If-Modified-Since"

class IfNoneMatchHeader(ft.EntityTagDict):
    """
    The If-None-Match request-header field is used with a 
    method to make it conditional. A client that has one or 
    more entities previously obtained from the resource can 
    verify that none of those entities is current by including 
    a list of their associated entity tags in the 
    If-None-Match header field.
    
    If-None-Match = "If-None-Match" ":" ( "*" | 1#entity-tag )
    """
    field_name = "If-None-Match"
    
class IfRangeHeader(ft.EntityTagOrHttpDate):    
    """
    If a client has a partial copy of an entity in its cache, 
    and wishes to have an up-to-date copy of the entire entity in 
    its cache, it could use the Range request-header with a 
    conditional GET (using either or both of If-Unmodified- 
    Since and If-Match.) However, if the condition fails because 
    the entity has been modified, the client would then 
    have to make a second request to obtain the entire current 
    entity-body. 

    The If-Range header allows a client to short-circuit the 
    second request. Informally, its meaning is if the entity 
    is unchanged, send me the part(s) that I am missing; 
    otherwise, send me the entire new entity. 
    
    If-Range = "If-Range" ":" ( entity-tag | HTTP-date )
    """
    field_name = "If-Range"

class IfUnmodifiedSinceHeader(ft.HttpDate):
    """
    The If-Unmodified-Since request-header field is used 
    with a method to make it conditional. If the requested 
    resource has not been modified since the time 
    specified in this field, the server SHOULD perform the 
    requested operation as if the If-Unmodified-Since 
    header were not present.

    If-Unmodified-Since = "If-Unmodified-Since" ":" HTTP-date
    """
    field_name = "If-Unmodifed-Since"

class IMHeader(ft.HttpTokenList):
    """
    The IM response-header field is used to indicate the 
    instance-manipulations, if any, that have been applied 
    to the instance represented by the response. 
    """
    field_name = "IM"
    normalize = staticmethod(string.lower)
    
class KeepAliveHeader(ft.ParamDict):
    """
    When the Keep-Alive connection-token has been transmitted with
    a request or a response, a Keep-Alive header field MAY also be
    included.
    """
    field_name = "Keep-Alive"
    
class LastModifiedHeader(ft.HttpDate):
    """
    The Last-Modified entity-header field indicates the 
    date and time at which the origin server believes the 
    variant was last modified.   
    
    Last-Modified = "Last-Modified" ":" HTTP-date
    """
    field_name = "Last-Modified"

class LocationHeader(ft.Uri):
    """
    The Location response-header field is used to redirect 
    the recipient to a location other than the Request-URI 
    for completion of the request or identification of a 
    new resource.

    Location = "Location" ":" absoluteURI
    """
    field_name = "Location"

class MaxForwardsHeader(ft.Int):
    """
    The Max-Forwards request-header field provides a 
    mechanism with the TRACE and OPTIONS methods to limit 
    the number of proxies or gateways that can forward the 
    request to the next inbound server.
    
    Max-Forwards = "Max-Forwards" ":" 1*DIGIT
    """
    field_name = "Max-Forwards"
        
class MeterHeader(ft.ParamDict):
    """
    The Meter general-header field is used to:
      - Negotiate the use of hit-metering and usage-limiting
        among origin servers and proxy caches.
      - Report use counts and reuse counts.    
    
    Meter = "Meter" ":" 0#meter-directive
    """
    field_name = "Meter"
    
class MIMEVersionHeader(ft.Token):
    """
    HTTP is not a MIME-compliant protocol. However, HTTP/1.1 
    messages MAY include a single MIME-Version general-header 
    field to indicate what version of the MIME protocol was 
    used to construct the message. Use of the MIME-Version 
    header field indicates that the message is in full 
    compliance with the MIME protocol (as defined in RFC 2045).

    MIME-Version   = "MIME-Version" ":" 1*DIGIT "." 1*DIGIT
    """
    field_name = "MIME-Version"
    
class OverwriteHeader(ft.HttpToken):
    """
    The Overwrite header specifies whether the server  
    should overwrite the state of a non-null destination 
    resource during a COPY or MOVE.
    
    Overwrite = "Overwrite" ":" ("T" | "F")
    """
    field_name = "Overwrite"
    normalize = staticmethod(string.upper)

class P3PHeader(ft.ParamDict):
    """
    The location of a P3P Policy reference File.
    
    p3p-header = 'P3P: ' p3p-header-field *(',' p3p-header-field)
    p3p-header-field = policy-ref-field | compact-policy-field | extension-field
    policy-ref-field = 'policyref="' URI-Reference '"'
    extension-field = toekn [ '=' (token | quoted-string ) ]
    """
    field_name = "P3P"
    force_quote = ['policyref', 'compact-policy']
    
class PragmaHeader(ft.ParamDict):
    """
    The Pragma general-header field is used to include 
    implementation-specific directives that might apply 
    to any recipient along the request/response chain.
    
    Pragma = "Pragma" ":" 1#pragma-directive 
    """
    field_name = "Pragma"
    
class ProxyAuthenticateHeader(ft.ChallengeList):
    """
    The Proxy-Authenticate response-header field MUST be 
    included as part of a 407 (Proxy Authentication Required) 
    response. The field value consists of a challenge that 
    indicates the authentication scheme and parameters 
    applicable to the proxy for this Request-URI.
    
    Proxy-Authenticate = "Proxy-Authenticate" ":" 1#challenge
    """
    field_name = "Proxy-Authenticate"

class ProxyAuthenticationInfoHeader(ft.ParamDict):
    """
    The Proxy-Authentication-Info header is used by the 
    proxy to communicate some information regarding the 
    successful authentication in the response.
    """
    field_name = "Proxy-Authentication-Info"
    
class ProxyAuthorizationHeader(ft.Credentials):
    """
    The Proxy-Authorization request-header field allows the 
    client to identify itself (or its user) to a proxy which 
    requires authentication. The Proxy-Authorization field 
    value consists of credentials containing the 
    authentication information of the user agent for the 
    proxy and/or realm of the resource being requested.
    """
    field_name = "Proxy-Authorization"

class PublicHeader(ft.HttpTokenList):
    """
    The Public response-header field lists the set of methods 
    supported by the server. The purpose of this field is 
    strictly to inform the recipient of the capabilities of 
    the server regarding unusual methods.
    
    Public = "Public" ":" 1#method
    """
    field_name = "Public"
    normalize = staticmethod(string.upper)

class RangeHeader(ft.ByteRangeList):
    """
    HTTP retrieval requests using conditional or unconditional 
    GET methods MAY request one or more sub-ranges of the 
    entity, instead of the entire entity, using the Range 
    request header, which applies to the entity returned as the 
    result of the request.
    
    Range = "Range" ":" ranges-specifier
    """
    field_name = "Range"

class RefererHeader(ft.Uri):
    """
    The Referer[sic] request-header field allows the client 
    to specify, for the server's benefit, the address (URI) 
    of the resource from which the Request-URI was obtained 
    (the "referrer", although the header field is misspelled.)
    
    Referer = "Referer" ":" ( absoluteURI | relativeURI ) 
    """
    field_name = "Referer"
    
class RetryAfterHeader(ft.Int):
    """
    The Retry-After response-header field can be used with a 
    503 (Service Unavailable) response to indicate how long 
    the service is expected to be unavailable to the requesting 
    client.
    
    Retry-After = "Retry-After" ":" ( HTTP-date | delta-seconds )
    """
    field_name = "Retry-After"

class ServerHeader(ft.ProductComment):
    """
    The Server response-header field contains information 
    about the software used by the origin server to handle 
    the request.
    
    Server = "Server" ":" 1*( product | comment ) 
    """
    field_name = "Server"

class SoapActionHeader(ft.Uri):
    """
    The SOAPAction HTTP request header field can be used to 
    indicate the intent of the SOAP HTTP request.
    """
    field_name = "SOAPAction"
    
class TEHeader(ft.StrParamDict):
    """
    The TE request-header field indicates what extension 
    transfer-codings it is willing to accept in the response 
    and whether or not it is willing to accept trailer fields 
    in a chunked transfer-coding.
    
    TE = "TE" ":" #( t-codings )
    """
    field_name = "TE"

class TimeoutHeader(ft.HttpToken):
    """
    Clients may include Timeout request headers in their 
    LOCK requests.
    
    TimeOut = "Timeout" ":" 1#TimeType
    TimeType = ("Second-" DAVTimeOutVal | "Infinite")
    """
    field_name = "Timeout"
    normalize = staticmethod(string.capitalize)

class TrailerHeader(ft.FieldNameList):
    """
    The Trailer general field value indicates that the given 
    set of header fields is present in the trailer of a message 
    encoded with chunked transfer-coding.
    
    Trailer = "Trailer" ":" 1#field-name
    """
    field_name = "Trailer"

class TransferEncodingHeader(ft.HttpTokenList):
    """
    The Transfer-Encoding general-header field indicates what 
    (if any) type of transformation has been applied to the 
    message body in order to safely transfer it between the 
    sender and the recipient. This differs from the 
    content-coding in that the transfer-coding is a property 
    of the message, not of the entity.
    
    Transfer-Encoding = "Transfer-Encoding" ":" 1#transfer-coding
    """
    field_name = "Transfer-Encoding"

class UpgradeHeader(ft.ProductComment):
    """
    The Upgrade general-header allows the client to specify 
    what additional communication protocols it supports and 
    would like to use if the server finds it appropriate to 
    switch protocols.
    
    Upgrade = "Upgrade" ":" 1#product
    """
    field_name = "Upgrade"

class UserAgentHeader(ft.ProductComment):
    """
    The User-Agent request-header field contains information 
    about the user agent originating the request.
    
    User-Agent = "User-Agent" ":" 1*( product | comment )
    """
    field_name = "User-Agent"

class VaryHeader(ft.FieldNameList):
    """
    The Vary field value indicates the set of request-header 
    fields that fully determines, while the response is fresh, 
    whether a cache is permitted to use the response to reply 
    to a subsequent request without revalidation.
    
    Vary = "Vary" ":" ( "*" | 1#field-name )
    """
    field_name = "Vary"

class ViaHeader(ft.ViaList):
    """
    The Via general-header field MUST be used by gateways and 
    proxies to indicate the intermediate protocols and 
    recipients between the user agent and the server on requests, 
    and between the origin server and the client on responses.
    
    Via = "Via" ":" 1#( received-protocol received-by [ comment ] )
    """
    field_name = "Via"

class WarningHeader(ft.WarningValueList):
    """
    The Warning general-header field is used to carry additional
    information about the status or transformation of a message 
    which might not be reflected in the message.
    
    Warning = "Warning" ":" 1#warning-value
    warning-value = warn-code SP warn-agent SP warn-text
                                           [SP warn-date]
    """
    field_name = "Warning"

class WWWAuthenticateHeader(ft.ChallengeList):
    """
    The WWW-Authenticate response-header field MUST be included 
    in 401 (Unauthorized) response messages. The field value 
    consists of at least one challenge that indicates the 
    authentication scheme(s) and parameters applicable to the 
    Request-URI.
    
    WWW-Authenticate = "WWW-Authenticate" ":" 1#challenge
    """
    field_name = "WWW-Authenticate"


    