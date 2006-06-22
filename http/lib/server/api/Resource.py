"""
http.server.api.Resource
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

from .base import PipelineComponent
from ... import status
from ...headers.registry import newField
import string

class Resource:
    """Base class for Resources."""
    children = {}                # child Resource classes
    def __init__(self, name=None, parent=None):
        self.name = name         # my path segment name
        self.parent = parent     # my parent's instance
        self.pipeline = [
            MethodDispatcher(self), 
        ]
        self.restoreState()


    def dereference(self, path):  # TODO: better name?
        """
        Given a sequence of path segments, return the appropriate Resource,
        instantiating if need be. Alternatively, raise a Status exception.
        Called by Server.
        """
        if not len(path):  # FIXME: empty path - foo vs. foo/
            return self
        elif path[0] in self.children.keys():
            return self.children[path[0]](name=path[0], parent=self)._dereference(path[1:])
        else:
            return self.getChild(path[0])._dereference(path[1:])
                
    def reference(self):
        """
        Return a URI for this resource.
        """
        segments = [self.name]
        parent = None # FIXME: figure out parent for reference
        while 1:
            segments.insert(0, parent.name)
            if isinstance(parent, Resource):
                parent = parent.parent
            else:
                break
        return "/".join(segments)    # FIXME: foo vs. foo/
               
    def getChild(self, name):
        """
        Given a child name, return an instantiated Resource.
        May be overridden.
        """
        raise status.NotFound()
        
    def storeState(self):
        pass
    
    def restoreState(self):
        pass

    def __del__(self):
        self.storeState()
        
        
class RequestDispatcher(PipelineComponent):
    def __init__(self, context):
        PipelineComponent.__init__(self, context)
        self.methods = filter(lambda a:a[0]!='_' and \
          callable(getattr(resource, a)), dir(context))
            
    def __call__(self, request, response):
        method_name = request.method
        if request.body is None:
            presented_type = None
        else:
            try:
                presented_type = request.headers['content-type'].value
            except KeyError:
                raise status.BadRequest()
        try:
            preferred_types = request.headers['accept'].value
        except:
            preferred_types = newField('accept', string="*/*")
        for preferred_type in preferred_types:
            try:
                method = self.methods[(method_name, presented_type, preferred_type)]
            except:
                continue            
        apply(method, (request, response))
         ### set content-type
        if hasattr(response.headers, 'Vary'):
            response.headers['Vary'].value.append('Accept')
        else:
            response.headers['Vary'].value = ['Accept']
        if response.headers['Content-Type'].has_key('q'):
            del response.headers['Content-Type'].params['q']
         

class MethodDispatcher(PipelineComponent):
    """
    Pipeline component to call the appropriate Resource method, based on
    HTTP method (and perhaps request media type).
    """
    def __init__(self, context):
        PipelineComponent.__init__(self, context)
        methods = filter(lambda a: a[0]!='_' and \
          callable(getattr(context, a)), dir(context))
        self.http_methods = filter(lambda a: a.isupper(), \
          filter(lambda a: "_" not in a, methods))

    def send_response(self, request, response):
        method_name = request.method
        if request.body != None:
            try:
                presented_type = request.headers['content-type'].value
            except KeyError:
                raise status.BadRequest()
            typed_method = "%s_%s" % (request.method, _norm_type(presented_type))
            if hasattr(self.context, typed_method):
                method_name = typed_method
            elif not hasattr(self.context, request.method):
                raise status.UnsupportedMediaType()  
        try:
            method = getattr(self.context, method_name)
        except AttributeError:
            mna = status.MethodNotAllowed()
            mna.headers['Allow'] = self.http_methods
            raise mna
        apply(method, (request, response))


class MethodHack(PipelineComponent):
    """
    Pipeline component to change the effective method based on
    query components. Must be used with POST.
    """
    def __call__(self, request, response):
        if request.method == 'POST' and \
          request.uri_query.has_key('http_method'):
            request.method = request.uri_query['http_method'][0]


# class ContentNegotiator(PipelineComponent):
#     """
#     Pipeline component to effect content negotiation of media type.
#     """
#     TO = re.compile("_TO_")
#     def __init__(self, resource):
#         self.resource = resource
#         self.tr_methods = filter(lambda a, r=resource: self.TO.search(a) and \
#           callable(getattr(r, a)), dir(resource))
# 
#     def __call__(self, request, response):
#         if request.uri_query.has_key('type'):   # type hack
#             acceptable_types = [{'VALUE': request.uri_query['type'][0]}]
#         else:
#             if not request.headers.has_key('Accept'):
#                 acceptable_types = [{'VALUE': '*/*'}]
#             else:
#                 acceptable_types = request.headers['Accept']
#                 acceptable_types.sort(sortByQValue)
#         acceptable_types.append(None)
#         in_arg = _norm_type(response.headers['Content-Type']['VALUE'])
#         available_tr = filter(
#           lambda a, i=in_arg: a[:len(i)]==i, self.tr_methods)
#         available_types = map(
#           lambda a, s=self: getattr(s.resource, a).content_type, available_tr)
#         available_types = map(lambda a, {'VALUE': a[0], 'q': a[1]}, available_types)  ### ugly
#         available_types.append(response.headers['Content-Type'])
#         available_types.sort(sortByQValue)
#         for acceptable_type in acceptable_types:
#             if acceptable_type == None:
#                 raise status.NotAcceptable()
#             if float(acceptable_type.get('q', '1')) == 0:
#                 continue
#             if acceptable_type['VALUE'] == "*/*": 
#                 out_type = available_types[0]
#                 break
#             elif acceptable_type['VALUE'][-2:] == "/*":
#                 out_type = filter(
#                   lambda a, 
#                   c=acceptable_type['VALUE'][:acceptable_type['VALUE'].index('/')]: 
#                 a['VALUE'][a['VALUE'].index('/')]==c, available_types)[0]
#                 break
#             elif _norm_type(acceptable_type['VALUE']) in \
#               map(lambda a, n=_norm_type: n(a['VALUE']), available_types):
#                 out_type = acceptable_type
#                 break
#             else:
#                 continue
#         if float(out_type.get('q', 1)) == 0:
#             raise status.NotAcceptable()
#         if out_type['VALUE'] == response.headers['Content-Type']['VALUE']:
#             if response.headers['Content-Type'].has_key('q'):
#                 del response.headers['Content-Type']['q']
#         else:
#             neg_method_name = "%s_TO_%s" % (in_arg, _norm_type(out_type['VALUE']))
#             neg_method = getattr(self.resource, neg_method_name)
#             response.body = apply(neg_method, (response.body))
#             ### set content-type
#             if hasattr(response.headers, 'Vary'):
#                response.headers['Vary'].append('Accept')
#             else:
#                 response.headers['Vary'] = ['Accept']
#             if response.headers['Content-Type'].has_key('q'):
#                 del response.headers['Content-Type']['q']
# 
#     
    
# Support functions
_type_normaliser = string.maketrans('+-/.','____')
def _norm_type(in_type):
    return in_type.translate(_type_normaliser).lower()