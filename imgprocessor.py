import os
import time
import sys
import logging.handlers
import logging
from PIL import Image
from configparser import ConfigParser
from configparser import ExtendedInterpolation
from pkg_resources import resource_stream, Requirement


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
        self.defaultscreen = config.get(section="config",option="defaultscreen")
        self.defaultband = config.get(section="config",option="defaultbandwidth")
        self.imagepath = config.get(section="config",option="path")
        #self.mylogger.setLevel(config.get(section="config",option="loglevel"))
        self.screens = dict(screenmix.split(",")  for screenmix in screenconfig.split(";"))
        self.bandwidth = dict(band.split(",") for band in bandconfig.split(";"))
        self.mylogger.info(msg="Done initialization")

    def generate(self,filename,size="320",bandwidth="*",returnFullpath=False):
        try:

            self.mylogger.info('Generating file {}'.format(filename))
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
            img.save(savefilename)
            self.mylogger.info("Saved file {} for {}".format(filename,savefilename))

            if returnFullpath:
                return fullpath
            else:
                return os.path.join(self.imagepath,savefilename)
                self.mylogger.info(msg="returned for file {}".format(filename))
        except NameError as filenotfound:
            raise NameError('File {} doesnt exist'.format(filename))
            self.mylogger.exception("Exception occurred in image generation for {}".format(filename))
        except Exception as genEx:
            self.mylogger.exception("Exception occurred in image generation for {}".format(filename))
        finally:
            self.mylogger.info("Completed")

    '''We will set the optimized value for image generation based on size & bandwidth'''
    def _getoptimizesizebasedonsizebandwidth(self,size,band):
        '''If the sizeinfo is not configured, send the highest sizeinfo available'''
        self.mylogger.info(msg='Size & bandwidth is {} & {}'.format(size,band))
        try:
            size = self.screens[str(size)]
            #print(size)
        except Exception:
            size = max({val:key for key, val in self.screens.items()})
            #self.mylogger.info('Size was not found and defaulting to size {}'.format(size))
        '''if input value isnt configured, send the highest bandwidth configured'''
        try:
            band = self.bandwidth[band.lower()]
            #print(band)
        except Exception:
            band =  max({val:key for key, val in self.bandwidth.items()})
            #self.mylogger.info('Bandwidth was not found and defaulting to size {}'.format(bandwidth))
        self.sumup = float(size) + float(band)
        self.mylogger.info('Sumup value is {}'.format(self.sumup))
        #print(self.sumup)
        if float(self.sumup) <= 4:
            self.sumup = 4
            return 0.22
        elif float(self.sumup) <= 7:
            '''I am sure screen is of medium size and bandwidth is around 2g'''
            self.sumup = 7
            return 0.33
        elif float(self.sumup) <=10:
            '''I know this is of medium resolution and high bandwidth or high res with low bandwidth'''
            self.sumup = 10
            return 0.44
        else:
            '''I am sure if the value is > 4, its either 3g, 4g etc with higher screensize'''
            self.sumup = 11
            return 0.5