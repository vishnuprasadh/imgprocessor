#!usr/bin/env python

from wsgiref.simple_server import make_server
from wsgiref.handlers import CGIHandler
import urllib as url
import cgi

import os
import time
import sys
import logging.handlers
import logging
import base64
from PIL import Image
from configparser import ConfigParser
from configparser import ExtendedInterpolation
from pkg_resources import resource_stream, Requirement
from io import BytesIO
from  io import StringIO


'''All configured bandwidth, screens will be initialized with a weightage'''
bandwidth = dict()
screens = dict()

'''Default screensize, band will be set once initialized'''
defaultscreen = {}
defaultband = {}

'''The root path for all images'''
imagepath = {}
sumup=0

'''Initialize the logger to log information'''
mylogger = logging.getLogger('Imagehandler')
handler = logging.handlers.RotatingFileHandler('imghandler.log','a',maxBytes=10000000,backupCount=5)
mylogger.addHandler(handler)

def application(environ,start_response):
    returnquerystring = ""
    response_body = []

    if environ["PATH_INFO"] == "/images/":

        params = cgi.parse_qs( environ["QUERY_STRING"])

        #response_body = ["{}:{}".format(k, v) for k,v  in environ.items()]
        response_body = '\n'.join(response_body)

        returnquerystring = "key:"

        filename=""
        '''default value'''
        size="320"
        bandwidth="2g"

        if any (params):
            filename = params.get("name")[0]
            returnquerystring += filename


        if  environ.has_key("size")  :
            size= environ["size"]
            returnquerystring += "_"
            returnquerystring.write(size)

        if environ.has_key("nw_type") :
            bandwidth= environ["nw_type"]
            returnquerystring += "_"
            returnquerystring.write(bandwidth)


        #resp = generate(filename,size,bandwidth)
        #response_body = imghandle.generate(filename,size,bandwidth)

        with open('/var/www/images/nasa.jpeg','r') as f:
            response_body =f.read()
            f.close()


        status = '200 OK'
        response_headers = [
            ('Content-Type', 'image/jpeg'),
            ('Content-Length', str(len(response_body))),
            ('Query_String',str(returnquerystring))]
        start_response(status,response_headers)

    return [response_body]


def generate(filename,ssize="320",band="*"):

    try:
        mylogger.info(msg="Starttime is {}".format(time.time()))
        config = ConfigParser()
        config._interpolation = ExtendedInterpolation()

        '''Resource based loading option.'''
        #resource = resource_stream(Requirement.parse('imgprocessor==0.01'),'config.cfg').read()
        #resource = resource.decode('UTF-8','replace')
        #print(resource)
        #config.read_string(resource)


        '''get executionpath'''
        dirname = os.path.dirname(os.path.realpath(__file__))
        config.read(os.path.join (dirname ,"config.cfg"))
        mylogger.info(msg="Dirname is {}".format(dirname))

        #print(config.keys())
        #print(config.sections())


        mylogger.info(msg="Dirname is in {}".format(os.path.join (dirname ,"config.cfg")))

        '''Initialize all the configurations like screensizes, bandconfig etc'''
        screenconfig = config.get(section="config",option="screensize")
        bandconfig = config.get(section="config",option="band")
        defaultscreen = config.get(section="config",option="defaultscreen")
        defaultband = config.get(section="config",option="defaultbandwidth")
        imagepath = config.get(section="config",option="path")
        #mylogger.setLevel(config.get(section="config",option="loglevel"))
        screens = dict(screenmix.split(",")  for screenmix in screenconfig.split(";"))
        bandwidth = dict(band.split(",") for band in bandconfig.split(";"))
        #print(screens)
        #print(bandwidth)
        mylogger.info(msg="Done initialization")


        imgfile = BytesIO()
        mylogger.info('Generating file {}'.format(filename))
        '''Expected name of the file to be generated'''
        scale = _getoptimizesizebasedonsizebandwidth(ssize, band, screens, bandwidth)
        savefilename = filename.split(".")[0] + "_" + str(sumup) + "." + filename.split(".")[1]
        savefilename = os.path.join(imagepath, savefilename )

        '''if filealready exist return file name'''
        if os.path.isfile(savefilename):
            img = Image.open(savefilename)
            img.save(imgfile,format="JPEG")
            '''encode it using base64 and return in asciformat'''
            base64encode=  base64.encodebytes(imgfile.getvalue())
            return base64encode.decode("ascii")

        '''Open the file if it isnt there and resize, send back the path'''

        '''Check if input fullpath leads to file, if not throw exception'''
        fullpath = os.path.join(imagepath, filename)
        if not os.path.isfile(fullpath):
            raise NameError('File not found')

        '''if fullpath is file, then open the same'''
        img = Image.open(fullpath, 'r')
        mylogger.info("Size of image is {}".format(img.size))
        img.thumbnail((int(img.size[0]*scale) , int(img.size[0]*scale)),Image.LANCZOS)
        '''saved locally'''
        img.save(savefilename,format="JPEG")

        '''load from bytes too'''
        img.save(imgfile,format="JPEG")
        '''encode it using base64 and return in asciformat'''
        base64encode = base64.encodebytes(imgfile.getvalue())
        return base64encode.decode('ascii')

        mylogger.info("Saved file {} for {}".format(filename,savefilename))
    except NameError as filenotfound:
        raise NameError('File {} doesnt exist'.format(filename))
        mylogger.exception("Exception occurred in image generation for {}".format(filename))
    finally:
        mylogger.info("Completed")


'''We will set the optimized value for image generation based on size & bandwidth'''
def _getoptimizesizebasedonsizebandwidth(size,band,screens,bandwidth):
    '''If the sizeinfo is not configured, send the highest sizeinfo available'''
    mylogger.info(msg='Size & bandwidth is {} & {}'.format(size,band))
    try:
        size = screens[str(size)]
    except Exception:
        size = max({val:key for key, val in screens.items()})
        #mylogger.info('Size was not found and defaulting to size {}'.format(size))
    '''if input value isnt configured, send the highest bandwidth configured'''
    try:
        band = bandwidth[band.lower()]
    except Exception:
        band =  max({val:key for key, val in bandwidth.items()})
        #mylogger.info('Bandwidth was not found and defaulting to size {}'.format(bandwidth))
    sumup = size + band
    mylogger.info('Sumup value is {}'.format(sumup))
    if float(sumup) <= 4:
        sumup = 4
        return 0.22
    elif float(sumup) <= 7:
        '''I am sure screen is of medium size and bandwidth is around 2g'''
        sumup = 7
        return 0.33
    elif float(sumup) <=10:
        '''I know this is of medium resolution and high bandwidth or high res with low bandwidth'''
        sumup = 10
        return 0.44
    else:
        '''I am sure if the value is > 4, its either 3g, 4g etc with higher screensize'''
        sumup = 11
        return 0.5




httpd = make_server('',8051,application)

httpd.serve_forever()

