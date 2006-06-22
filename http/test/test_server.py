#!/usr/bin/env python2.5

from ..lib.server.api.Resource import Resource
from ..lib.server.adapters.CGI import CGI

class Test(Resource):
    
    def GET(self, request, response):
        response.body = "foo"
    
server = CGI(Test, '')
server.serve()