#!/usr/bin/env python
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
import cgi

'''the class is used for processing of the image dynamically and accepts the name of the original image
the screensize and the bandwidth.
Based on these values, the program will do simple logic of sending the most optimal size image and uses
the optimal PIL-SIMD based Image generation which is faster than most other tools including Imagemagica by approx 10-15times
'''
class wsgiimagenerator(object):
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

    def generate(self,filename,ssize="320",band="*"):

        try:
            self.mylogger.info(msg="Starttime is {}".format(time.time()))
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
            self.mylogger.info(msg="Dirname is {}".format(dirname))

            #print(config.keys())
            #print(config.sections())


            self.mylogger.info(msg="Dirname is in {}".format(os.path.join (dirname ,"config.cfg")))

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
            self.mylogger.info(msg="Done initialization")


            imgfile = BytesIO()
            self.mylogger.info('Generating file {}'.format(filename))
            '''Expected name of the file to be generated'''
            scale = self._getoptimizesizebasedonsizebandwidth(ssize, band, screens, bandwidth)
            savefilename = filename.split(".")[0] + "_" + str(self.sumup) + "." + filename.split(".")[1]
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
            self.mylogger.info("Size of image is {}".format(img.size))
            img.thumbnail((int(img.size[0]*scale) , int(img.size[0]*scale)),Image.LANCZOS)
            '''saved locally'''
            img.save(savefilename,format="JPEG")

            '''load from bytes too'''
            img.save(imgfile,format="JPEG")
            '''encode it using base64 and return in asciformat'''
            base64encode = base64.encodebytes(imgfile.getvalue())
            return base64encode.decode('ascii')

            self.mylogger.info("Saved file {} for {}".format(filename,savefilename))
        except NameError as filenotfound:
            raise NameError('File {} doesnt exist'.format(filename))
            self.mylogger.exception("Exception occurred in image generation for {}".format(filename))
        finally:
            self.mylogger.info("Completed")


    '''We will set the optimized value for image generation based on size & bandwidth'''
    def _getoptimizesizebasedonsizebandwidth(self,size,band,screens,bandwidth):
        '''If the sizeinfo is not configured, send the highest sizeinfo available'''
        self.mylogger.info(msg='Size & bandwidth is {} & {}'.format(size,band))
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
        self.mylogger.info('Sumup value is {}'.format(sumup))
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


