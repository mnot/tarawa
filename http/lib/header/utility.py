"""
http.header.utility - HTTP header utility functions.
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

linesep = "\r\n"

# sorting functions

def sortByQValue(a, b):
    """Sort lists of x by x.params['q']"""
    return cmp(float(b.params.get('q', '1.0')), float(a.params.get('q', '1.0')))

def sortMediaTypes(a, b):
    """Sort lists of Content-Types by QValue"""
    aval = float(a.params.get('q', '1.0'))
    bval = float(b.params.get('q', '1.0'))
    if aval == bval:
        aval = len(a)
        bval = len(b)
    if aval == bval:
        if a['VALUE'][-1] == '*': aval = 0.001
        if b['VALUE'][-1] == '*': bval = 0.001
    if aval == bval:
        if a['VALUE'] == '*/*': aval = 0
        if b['VALUE'] == '*/*': bval = 0
    return cmp(bval, aval)

def sortQValLast(a, b):
    """Sort lists of (x, y) tuples so that an x of 'q' is always last."""
    if a[0] == 'q': return 1
    elif b[0] == 'q': return -1
    else: return 0    
    