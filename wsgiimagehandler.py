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
mylogger.setLevel("INFO")


def application(environment,start_response):
    '''
    This application is standalone server which internally calls the class:imghandler that outputs the byte of image without local storage.
    In case you need the path to the file or json, will directly need to integrate with  class: imgprocessor or class:imgjsonhandler
    Querystring accepted are below. Only filename is mandatory.
    --name = "Path or name of the image". Note that imagehandler has a path config which will be used with this value to load the file
    --width = width of image to generate
    --height = height of image to generate
    --fsize = forcesize the image i.e. if 1, it will not keep aspect ratio and blindly resizes image, else it would keep aspect ratio and generate image based on WxH given

    Header - Both are optional headers used more for native app optimizations:
    --screensize - This is the screensize used for dynamic scaledown of image would happen. Use this for mobile apps.
    Optimization logic written for values of 320, 360,480, 540, 1080, 720, 640, 240.
    --nw_type : This can be 2g,3g,4g or *. This is network type , * means anything outside 2g,3g,4g used more for desktops

    if both screensize,nw_type with width & height is given, width & height is considered along with nw_type.
    if width & height with nw_type is given then the same would be considered for image optimization in terms of size.
    if none are given screensize is assumed to be 1080, nw_type = *

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
    forcesize= False

    try:
        if environment["PATH_INFO"] == "/images/":

            '''Parse querystring tp get the values'''
            params = cgi.parse_qs(environment["QUERY_STRING"])

            '''resolve Image name, height,width & fsize in querystring'''
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
                        forcesize = params.get("fsize")[0]
                        '''if input value is other than 0 or 1, set forcesize as 0 i.e.false'''
                        if not (forcesize == "1"):
                            forcesize= False
                        else:
                            forcesize = True
                    except Exception as ex :
                        mylogger.error(ex)
                        forcesize =False

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
            mylogger.info("Gen image for name:{},ssize:{},bwidth:{},w:{},h:{},force:{}".format(filename,screensize,bwidth,width,height,forcesize))
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
        mylogger.error(genex)
        response_headers = [
            #('Content-Type', 'image/jpeg'),
            ("Content-Type", "text/html"),
            ('Content-Length', str(len(response_body))),
            ('Server', "Encrypt"),
            ('Response_QS',str(returnquerystring))]
    finally:
        start_response(status,response_headers)
        mylogger.info("Just sending out the response now")
        return [response_body]


'''Make the server -note that the requests shoudl come to this port'''
httpd = make_server('',8051,application)
'''Continue to listen on this server forever'''
httpd.serve_forever()

