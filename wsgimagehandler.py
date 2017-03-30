#!usr/bin/env python

from wsgiref.simple_server import make_server
from wsgiref.handlers import CGIHandler
import urllib as url
import cgi

from io import StringIO

def application(environ,start_response):
    returnquerystring = StringIO()
    response_body = []

    if environ["PATH_INFO"] == "/images/":

        response_body = ["{}:{}".format(k, v) for k,v  in environ.items()]
        response_body = '\n'.join(response_body)

        returnquerystring.write("key:")
        returnquerystring.write("nasa.jpeg")
        returnquerystring.write("_")

        '''
        queryparams = dict()
        queryparams = cgi.parse_qs(environ["QUERY_STRING"])


        filename,size,bandwidth=""

        if not queryparams is None:
            filename = queryparams.get('name', "")[0]
            returnquerystring.write("key:")
            returnquerystring.write(filename)
            returnquerystring.write("_")
        if not environ["size"] is None:
            size= environ["size"]
            returnquerystring.write(size)
            returnquerystring.write("_")
        if not environ["nw_type"] is None:
            bandwidth= environ["band"]
            returnquerystring.write(bandwidth)
        '''

        status = '200 OK'
        response_headers = [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(response_body))),
            ('Query_String',returnquerystring.getvalue())]
        start_response(status,response_headers)

    return [response_body]


httpd = make_server('',8051,application)

httpd.serve_forever()
