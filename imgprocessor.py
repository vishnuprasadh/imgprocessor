import os
import time
import sys
import numpy as np
import logging.handlers
import logging
import argparse
from PIL import Image, ImageEnhance
from configparser import ConfigParser
from configparser import ExtendedInterpolation
from pkg_resources import resource_stream, Requirement
import pkg_resources
args = argparse.ArgumentParser(prog='python -m imgprocessor',
                               description='Given a filename with screensize, bandwidth the program generates the file and provides the output of the filepath with name',
                               add_help='provide filename as firstparameter, screen w=width e.g. 720 or 1024 etc, bandwidth as third parameter i.e. 2g,3g,4g or * in case of default'
                               )
args.add_argument('-f', '--file', required=True, help='The name of image file to generate')
args.add_argument('-s', '--size' ,required=False, default=740 ,help='The size of client device, defaults to 740')
args.add_argument('-b', '--bandwidth',required=False, default='*' ,help='The bandwidth of device, defaults to high bandwidth.You can give 2g,3g,4g or *')
args.add_argument('-r', '--returnpath',required=False, default=False, help='If you need full returnpath provide true here' )


class imgprocessor(object):
    '''the class is used for processing of the image dynamically and accepts the name of the original image
    the screensize and the bandwidth.
    Based on these values, the program will do simple logic of sending the most optimal size image and uses
    the optimal PIL-SIMD based Image generation which is faster than most other tools including Imagemagica by approx 10-15times
    '''

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

    def __init__(self):
        self.mylogger.info('starttime is {}'.format(time.time()))
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
        print(config.keys())
        print(config.sections())


        #self.mylogger.info('Dirname is in {}'.format(os.path.join (dirname ,"config.cfg")))

        '''Initialize all the configurations like screensizes, bandconfig etc'''
        screenconfig = config.get(section="config",option="screensize")
        bandconfig = config.get(section="config",option="band")
        self.defaultscreen = config.get(section="config",option="defaultscreen")
        self.defaultband = config.get(section="config",option="defaultbandwidth")
        self.imagepath = config.get(section="config",option="path")
        self.mylogger.setLevel(config.get(section="config",option="loglevel"))
        self.screens = dict(screenmix.split(",")  for screenmix in screenconfig.split(";"))
        self.bandwidth = dict(band.split(",") for band in bandconfig.split(";"))
        self.mylogger.info("Done initialization")

    def generate(self,filename,size="320",bandwidth="*",returnFullpath=False):
        try:

            self.mylogger.info('Generating file {} at {}'.format(filename,time.time()))
            '''Expected name of the file to be generated'''
            scale = self._getoptimizesizebasedonsizebandwidth(size, bandwidth)
            savefilename = filename.split(".")[0] + "_" + str(self.sumup) + "." + filename.split(".")[1]
            savefilename = os.path.join(self.imagepath, savefilename )

            '''if filealready exist return file name'''
            if os.path.isfile(savefilename):
                return savefilename
            '''Open the file if it isnt there and resize, send back the path'''

            '''Check if input fullpath leads to file, if not throw exception'''
            fullpath = os.path.join(self.imagepath, filename)
            if not os.path.isfile(fullpath):
                raise NameError('File not found')

            '''if fullpath is file, then open the same'''
            img = Image.open(fullpath, 'r')
            self.mylogger.info("Size of image is {}".format(img.size))
            img.thumbnail((int(img.size[0]*scale) , int(img.size[0]*scale)),Image.LANCZOS)
            #img = img.resize((int(img.size[0]*scale) , int(img.size[0]*scale)),Image.LANCZOS)
            img.save(savefilename)
            self.mylogger.info("Saved file {} for {}".format(filename,savefilename))

            if returnFullpath:
                return fullpath
            else:
                return os.path.join(self.imagepath,savefilename)
                self.mylogger.info("returned for file {}".format(filename))
        except NameError as filenotfound:
            raise NameError('File {} doesnt exist'.format(fullpath))
            self.mylogger.exception(msg='Exception occurred in image generation for {}'.format(filename),exc_info=filenotfound)
        except Exception as genEx:
            '''logging exception'''
            self.mylogger.exception(msg='Exception occurred in image generation for {}'.format(filename),exc_info=genEx)
        finally:
            '''we will use it if required'''


    '''We will set the optimized value for image generation based on size & bandwidth'''
    def _getoptimizesizebasedonsizebandwidth(self,size,bandwidth):
        '''If the sizeinfo is not configured, send the highest sizeinfo available'''
        self.mylogger.info('Size & bandwidth is {} & {}'.format(size,bandwidth))
        try:
            sizeinfo = self.screens[str(size)]
        except Exception:
            sizeinfo = max({val:key for key, val in self.screens.items()})
            self.mylogger.info('Size was not found and defaulting to size {}'.format(sizeinfo))
        '''if input value isnt configured, send the highest bandwidth configured'''
        try:
            bandinfo = self.bandwidth[bandwidth.lower()]
        except Exception:
            bandinfo =  max({val:key for key, val in self.bandwidth.items()})
            self.mylogger.info('Bandwidth was not found and defaulting to size {}'.format(bandinfo))
        self.sumup = int(sizeinfo) + int(bandinfo)
        self.mylogger.info('Sumup value is {}'.format(self.sumup))
        if self.sumup >= 4:
            '''I am sure if the value is > 4, its either 3g, 4g etc with higher screensize'''
            self.sumup = 3
            return 0.75
        elif self.sumup <= 2:
            '''I am sure if the value is < 2, it is lower res with low bandwidth'''
            self.sumup = 2
            return 0.3
        else:
            '''Else it is 2'''
            self.sumup=1
            return 0.5


'''We need this to enable commandline capabilities'''
if __name__ == '__main__':
    pargs = args.parse_args()
    img = imgprocessor()
    img.generate(pargs.file, pargs.size, pargs.bandwidth, pargs.returnpath)


