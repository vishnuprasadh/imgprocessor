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
    response_body = "Oops,we are sorry!"
    status = '200 OK'

    '''initialize the key variables we would be using for passing imagegenerator'''
    filename = ""
    screensize = ""
    bwidth = ""
    width =0
    height = 0
    '''default forcesize is not done and aspect is maintained'''
    forcesize=False

    try:
        if environment["PATH_INFO"] == "/images/":

            '''Parse querystring tp get the values'''
            params = cgi.parse_qs(environment["QUERY_STRING"])

            '''resolve imagename in querystring'''
            if any(params):
                filename = params.get("name")[0]
                if not(params.get("width") == "NoneType"):
                    try:
                        width = int(params.get("width")[0])
                    except:
                        width =0

                if not( params.get("height") =="NoneType") :
                    try:
                        height = int(params.get("height")[0])
                    except:
                        height =0

                if not( params.get("fsize") =="NoneType") :
                    try:
                        forcesize = bool(params.get("fsize")[0])
                    except:
                        forcesize =0

            '''resolve all header info which has screensize & bandwidth'''
            if environment.get("HTTP_NW_TYPE") == 'NoneType':
                bwidth = "2g"
            else:
                bwidth = str(environment.get("HTTP_NW_TYPE"))

            if environment.get("HTTP_SCREENSIZE") == 'NoneType':
                screensize = "320"
            else:
                screensize = str(environment.get("HTTP_SCREENSIZE"))

            img = imagehandler()
            response_body=img.generate(filename,ssize= screensize,band= bwidth,width= width,height=height,forcesize=forcesize)

            '''Set the return key'''
            if (height > 0 or width > 0):
                if len(bwidth)==0 or bwidth =="None":
                    returnquerystring = "{}_{}x{}".format(filename,width,height)
                else:
                    returnquerystring = "{}_{}x{}_{}".format(filename,width,height,bwidth)
            else:
                if not (screensize =="None") and not(bwidth =="None") :
                    returnquerystring ="{}_{}_{}".format(filename,screensize,bwidth)
                elif not(screensize =="None") and bwidth =="None":
                    returnquerystring = "{}_{}".format(filename, screensize)
                elif screensize =="None" and not (bwidth =="None"):
                    returnquerystring = "{}_{}".format(filename, bwidth)
                else:
                    returnquerystring = filename


        '''In the response header, we will also set imagekey for use in varnish and other edgecache servers'''
        response_headers = [
            ('Content-Type', 'image/jpeg'),
            #("Content-Type","text/html"),
            ('Content-Length', str(len(response_body))),
            ('Server', "Encrypt"),
            ('imagekey', str(returnquerystring))]

    except Exception as genex:
        status = '400 Bad Request'
        response_body = str(genex)
        response_headers = [
            #('Content-Type', 'image/jpeg'),
            ("Content-Type", "text/html"),
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

