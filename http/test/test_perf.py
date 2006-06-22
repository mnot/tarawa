#!/usr/bin/env python2.5

from ..lib import message
from ..lib.header import fields
import time, profile

def invoke(s):
	req = message.Request()
	req.request_line = "GET /foobar/baz HTTP/1.1"
	req.headers.parseString(s)
	o = str(req)
	res = message.Request()
	res.status_line = "HTTP/1.0 200 OK"
	res.headers.parseString(s)
	res.body = "12345"
	o = str(res)
	
s =	"""Host: www.example.com
User-Agent: foo/1.0 (baz)
Content-Length: 155
Foo: Bar"""
 
def test(t):
	n = 0
	while n < t:
		invoke(s)
		n += 1

t = 5000
a = time.time()
#profile.run('test(t)')
test(t)
b = time.time()

print "%i ops/sec" % (t / (b - a))
