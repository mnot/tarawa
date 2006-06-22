"""
http.status - HTTP response messages, one for each status code. 

May be raised as exceptions.
"""

__license__ = """
Copyright (c) 2001-2006 Mark Nottingham <mnot@pobox.com>

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

from .message import Response

# TODO: DAV - 422 Unprocessable Entity, 423 Locked, 424 Failed Dependency, 507 Insufficient Storage
# TODO: AuthorityLookupFailed, NetworkFailed

lookup = {}

class _statusLookup(type):
    """Populate lookup with a status_code -> object name map. My head hurts."""
    def __new__(mcs, name, bases, props):
        cls = super(_statusLookup, mcs).__new__(mcs, name, bases, props)
        try:
            assert props['status_code'] != None
            lookup[props['status_code']] = cls
        except:
            pass
        return cls

class StatusException(Exception):
    """
    Allows a Status to be raised as an Exception.
    
    @ivar message the status response message being raised 
    @type message: Response
    """
    def __init__(self, message):
        self.message = message

class Status(Response): # TODO: what is the real relationship to Response?
    """
    Base class for status responses.
    
    @cvar has_body: whether the status code allows a response body entity
    @type has_body: Boolean
    @ivar exception: the StatusException wrapper for this status repsonse
    @type exception: StatusException
    """
    __metaclass__ = _statusLookup
    has_body = True
    def __init__(self, headers=None, body=None):
        Response.__init__(self)
        if headers != None:
            self.headers.update(headers)
        self.body = body
        self.exception = StatusException(self)
                
class Informational(Status):
    pass
    
class Continue(Informational):
    """
    The client SHOULD continue with its request. This interim
    response is used to inform the client that the initial part
    of the request has been received and has not yet been
    rejected by the server.
    """
    status_code = 100
    status_phrase = "Continue"
    has_body = False

class SwitchingProtocols(Informational):
    """ 
    The server understands and is willing to comply with the
    client's request, via the Upgrade message header field (section
    14.42), for a change in the application protocol being used on
    this connection.
    """
    status_code = 101
    status_phrase = "Switching Protocols"
    has_body = False

class Processing(Informational):
    # TODO: docstring
    status_code = 102
    status_phrase = "Processing"
    has_body = False # TODO: processing has_body

class Successful(Status):
    pass

class OK(Successful):
    """The request has succeeded."""
    status_code = 200
    status_phrase = "OK"
    
class Created(Successful):
    """
    The request has been fulfilled and resulted in a new resource 
    being created.
    """
    status_code = 201
    status_phrase = "Created"

class Accepted(Successful):
    """
    The request has been accepted for processing, but the
    processing has not been completed.
    """
    status_code = 202
    status_phrase = "Accepted"
    
class NonAuthoritativeInformation(Successful):
    """
    The returned metainformation in the entity-header is not
    the definitive set as available from the origin server,
    but is gathered from a local or a third-party copy.
    """
    status_code = 203
    status_phrase = "Non-Authoritative Information"
    
class NoContent(Successful):
    """
    The server has fulfilled the request but does not need to
    return an entity-body, and might want to return updated
    metainformation.
    """
    status_code = 204
    status_phrase = "No Content"
    has_body = False
    
class ResetContent(Successful):
    """
    The server has fulfilled the request and the user agent
    SHOULD reset the document view which caused the request to
    be sent.
    """
    status_code = 205
    status_phrase = "Reset Content"
    has_body = False
    
class PartialContent(Successful):
    """
    The server has fulfilled the partial GET request for the 
    resource.
    """
    status_code = 206
    status_phrase = "Partial Content"


class MultiStatus(Successful):
    # TODO: docstring
    status_code = 207
    status_phrase = "Multi-Status"
    has_body = False # TODO: has_body?

class Redirection(Status):
    pass

class MultipleChoices(Redirection):
    """
    The requested resource corresponds to any one of a set of
    representations, each with its own specific location, and
    agent-driven negotiation information (section 12) is being
    provided so that the user (or user agent) can select a
    preferred representation and redirect its request to that
    location.
    """
    status_code = 300
    status_phrase = "Multiple Choices"

class MovedPermanently(Redirection):
    """
    The requested resource has been assigned a new permanent URI
    and any future references to this resource SHOULD use one of
    the returned URIs.
    """
    status_code = 301
    status_phrase = "Moved Permanently"

class Found(Redirection):
    """
    The requested resource resides temporarily under a different
    URI.
    """
    status_code = 302
    status_phrase = "Found"
    
class SeeOther(Redirection):
    """
    The response to the request can be found under a different
    URI and SHOULD be retrieved using a GET method on that
    resource.
    """
    status_code = 303
    status_phrase = "See Other"
    
class NotModified(Redirection):
    """
    If the client has performed a conditional GET request and
    access is allowed, but the document has not been modified,
    the server SHOULD respond with this status code.
    """
    status_code = 304
    status_phrase = "Not Modified"
    has_body = False
    
class UseProxy(Redirection):
    """
    The requested resource MUST be accessed through the proxy
    given by the Location field.
    """
    status_code = 305
    status_phrase = "Use Proxy"
    has_body = False
    
class TemporaryRedirect(Redirection):
    """
    The requested resource resides temporarily under a different
    URI.
    """
    status_code = 307    
    status_phrase = "Temporary Redirect"

class ClientError(Status):
    pass
    
class BadRequest(ClientError):
    """
    The request could not be understood by the server due to
    malformed syntax.    
    """
    status_code = 400
    status_phrase = "Bad Request"

class Unauthorized(ClientError):
    """The request requires user authentication."""
    status_code = 401
    status_phrase = "Unauthorized"
    
class PaymentRequired(ClientError):
    """This code is reserved for future use."""
    status_code = 402
    status_phrase = "Payment Required"

class Forbidden(ClientError):
    """
    The server understood the request, but is refusing to 
    fulfill it.
    """
    status_code = 403
    status_phrase = "Forbidden"
    
class NotFound(ClientError):
    """
    The server has not found anything matching the Request-URI.
    """
    status_code = 404
    status_phrase = "Not Found"

class MethodNotAllowed(ClientError):
    """
    The method specified in the Request-Line is not allowed
    for the resource identified by the Request-URI.
    """
    status_code = 405
    status_phrase = "Method Not Allowed"
    
class NotAcceptable(ClientError):
    """
    The resource identified by the request is only capable of
    generating response entities which have content
    characteristics not acceptable according to the accept
    headers sent in the request.
    """
    status_code = 406
    status_phrase = "Not Acceptable"
    
class ProxyAuthenticationRequired(ClientError):
    """
    This code is similar to 401 (Unauthorized), but
    indicates that the client must first authenticate itself
    with the proxy.
    """
    status_code = 407
    status_phrase = "Proxy Authentication Required"
    
class RequestTimeout(ClientError):
    """
    The client did not produce a request within the time
    that the server was prepared to wait.
    """
    status_code = 408
    status_phrase = "Request Timeout"

class Conflict(ClientError):
    """
    The request could not be completed due to a conflict
    with the current state of the resource.
    """
    status_code = 409
    status_phrase = "Conflict"
    
class Gone(ClientError):
    """
    The requested resource is no longer available at the
    server and no forwarding address is known.
    """
    status_code = 410
    status_phrase = "Gone"
    
class LengthRequired(ClientError):
    """
    The server refuses to accept the request without a
    defined Content-Length.
    """
    status_code = 411
    status_phrase = "Length Required"
    
class PreconditionFailed(ClientError):
    """
    The precondition given in one or more of the
    request-header fields evaluated to false when it was
    tested on the server.
    """
    status_code = 412    
    status_phrase = "Precondition Failed"
   
class RequestEntityTooLarge(ClientError):
    """
    The server is refusing to process a request because the
    request entity is larger than the server is willing or
    able to process.
    """
    status_code = 413
    status_phrase = "Request Entity Too Large"
    
class RequestURITooLong(ClientError):
    """
    The server is refusing to service the request because
    the Request-URI is longer than the server is willing to
    interpret.
    """
    status_code = 414
    status_phrase = "Request-URI Too Long"
    
class UnsupportedMediaType(ClientError):
    """
    The server is refusing to service the request because
    the entity of the request is in a format not supported
    by the requested resource for the requested method.
    """
    status_code = 415
    status_phrase = "Unsupported Media Type"
    
class RequestedRangeNotSatisfiable(ClientError):
    """
    A server SHOULD return a response with this status code
    if a request included a Range request-header field
    (section 14.35) , and none of the range-specifier values
    in this field overlap the current extent of the selected
    resource, and the request did not include an If-Range
    request-header field.
    """
    status_code = 416
    status_phrase = "Requested Range Not Satisfiable"
    
class ExpectationFailed(ClientError):
    """
    The expectation given in an Expect request-header field (see
    section 14.20) could not be met by this server, or, if the
    server is a proxy, the server has unambiguous evidence that
    the request could not be met by the next-hop server.
    """
    status_code = 417    
    status_phrase = "Expectation Failed"

class ServerError(Status):
    pass
    
class InternalServerError(ServerError):
    """
    The server encountered an unexpected condition which
    prevented it from fulfilling the request.
    """
    status_code = 500
    status_phrase = "Internal Server Error"

class NotImplemented(ServerError):  ### Careful not to clash with built-in!
    """
    The server does not support the functionality required
    to fulfill the request.
    """
    status_code = 501
    status_phrase = "Not Implemented"

class BadGateway(ServerError):
    """
    The server, while acting as a gateway or proxy, received
    an invalid response from the upstream server it accessed
    in attempting to fulfill the request.
    """
    status_code = 502
    status_phrase = "Bad Gateway"
    
class ServiceUnavailable(ServerError):
    """
    The server is currently unable to handle the request due
    to a temporary overloading or maintenance of the server.
    """
    status_code = 503
    status_phrase = "Service Unavailable"
    
class GatewayTimeout(ServerError):
    """
    The server, while acting as a gateway or proxy, did not
    receive a timely response from the upstream server
    specified by the URI (e.g. HTTP, FTP, LDAP) or some
    other auxiliary server (e.g. DNS) it needed to access in
    attempting to complete the request.
    """
    status_code = 504
    status_phrase = "Gateway Timeout"
    
class HTTPVersionNotSupported(ServerError):
    """
    The server does not support, or refuses to support, the
    HTTP protocol version that was used in the request
    message.
    """
    status_code = 505
    status_phrase = "HTTP Version Not Supported"
lookup[505] = HTTPVersionNotSupported    
