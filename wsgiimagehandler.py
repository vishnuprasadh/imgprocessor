#!usr/bin/env python

from wsgiref.simple_server import make_server
from wsgiref.handlers import CGIHandler
import io
from mod_wsgi import server
from imagehandler import imagehandler
import cgi
import logging
import logging.handlers

'''Initialize the logger to log information'''
mylogger = logging.getLogger('Imagehandler')
handler = logging.handlers.RotatingFileHandler('imghandler.log','a',maxBytes=10000000,backupCount=5)
mylogger.addHandler(handler)


def application(environment,start_response):
    '''
    This application is standalone server which internally calls the class:imghandler that outputs the byte of image without local storage.
    In case you need the path to the file or json, will directly need to integrate with  class: imgprocessor or class:imgjsonhandler
    '''

    returnquerystring = ""
    response_body = []
    status = '200 OK'

    '''initialize the key variables we would be using for passing imagegenerator'''
    filename = ""
    screensize = ""
    bwidth = ""

    try:
        if environment["PATH_INFO"] == "/images/":

            '''Parse querystring tp get the values'''
            params = cgi.parse_qs(environment["QUERY_STRING"])

            '''resolve imagename in querystring'''
            if any(params):
                filename = params.get("name")[0]

            '''resolve all header info which has screensize & bandwidth'''
            if environment.get("HTTP_NW_TYPE") == 'NoneType':
                bwidth = "2g"
            else:
                bwidth = environment.get("HTTP_NW_TYPE")

            if environment.get("HTTP_SCREENSIZE") == 'NoneType':
                screensize = "320"
            else:
                screensize = environment.get("HTTP_SCREENSIZE")

            img = imagehandler()
            response_body=img.generate(filename,screensize,bwidth)

            #response_body = generate(filename,screensize,bwidth)

            returnquerystring ="{}_{}_{}".format(filename,screensize,bwidth)

        '''In the response header, we will also set imagekey for use in varnish and other edgecache servers'''
        response_headers = [
            ('Content-Type', 'image/jpeg'),
            # ("Content-Type","text/html"),
            ('Content-Length', str(len(response_body))),
            ('Server', "Encrypt"),
            ('imagekey', str(returnquerystring))]

    except Exception as genex:
        status = '400 Bad Request'
        response_body = str(genex)
        response_headers = [
            ('Content-Type', 'image/jpeg'),
            ('Content-Length', str(len(response_body))),
            ('Server', "Encrypt"),
            ('Response_QS',str(returnquerystring))]
    finally:
        start_response(status,response_headers)
        return [response_body]


'''Make the server -note that the requests shoudl come to this port'''
httpd = make_server('',8051,application)
'''Continue to listen on this server forever'''
httpd.serve_forever()

