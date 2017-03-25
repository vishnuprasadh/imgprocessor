import os
import time
import numpy as np
import logging.handlers
import logging
from PIL import Image, ImageEnhance
from configparser import ConfigParser


class imgprocessor:
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
        config.read("config.ini")
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
            savefilename = filename.split(".")[0] + "_" + str(self.sumup) + "." + filename.split(".")[1]
            savefilename = os.path.join(self.imagepath, savefilename )
            scale = self._getoptimizesizebasedonsizebandwidth(size,bandwidth)

            '''if filealready exist return file name'''
            if os.path.isfile(savefilename):
                return savefilename

            '''Open the file if it isnt there and resize, send back the path'''
            fullpath = os.path.join(self.imagepath, filename);
            img = Image.open(fullpath, 'r')
            self.mylogger.info("Size of image is {}".format(img.size))
            img = img.resize((int(img.size[0]*scale) , int(img.size[0]*scale)),Image.LANCZOS)
            img.save(savefilename)
            self.mylogger.info("Saved file {} for {}".format(filename,savefilename))

            if returnFullpath:
                return fullpath
            else:
                return os.path.join(self.imagepath,savefilename)
                self.mylogger.info("returned for file {}".format(filename))
        except Exception as genEx:
            '''logging exception'''
            self.mylogger.exception(msg='Exception occurred in image generation for {}'.format(filename),exc_info=genEx)
        finally:
            '''we will use it if required'''
            #self.mylogger.info('Exiting the generate method for file {} at {}, processtime - {}'.format(filename, time.time()))


    '''We will set the optimized value for image generation based on size & bandwidth'''
    def _getoptimizesizebasedonsizebandwidth(self,size,bandwidth):
        '''If the sizeinfo is not configured, send the highest sizeinfo available'''
        try:
            sizeinfo = self.screens[str(size)]
        except Exception:
            sizeinfo = max({val:key for key, val in self.screens})
            self.mylogger.info('Size was not found and defaulting to size {}'.format(sizeinfo))
        '''if input value isnt configured, send the highest bandwidth configured'''
        try:
            bandinfo = self.bandwidth[bandwidth.lower()]
        except Exception:
            bandinfo =  max({val:key for key, val in self.bandwidth})
            self.mylogger.info('Bandwidth was not found and defaulting to size {}'.format(bandinfo))
        self.sumup = int(sizeinfo) + int(bandinfo)
        self.mylogger.info('Sumup value is {}'.format(self.sumup))
        if self.sumup >= 4:
            '''I am sure if the value is > 4, its either 3g, 4g etc with higher screensize'''
            return 1
        elif self.sumup <= 2:
            '''I am sure if the value is < 2, it is lower res with low bandwidth'''
            return 0.3
        else:
            '''Else it is 2'''
            return 0.5



h = imgprocessor()
items = 100
tim1 = time.time()
for i in range(items):
    start = time.time()
    ind = np.random.randint(1,6,1)
    if ind == 1:
        h.generate("pictdkfwm101.jpg",720,'2g')
    elif ind == 2:
         h.generate("pictdkfwm101.jpg", 320,'2g')
    elif ind == 3:
        h.generate("pictdkfwm101.jpg", 900, '3g')
    elif ind == 4:
        h.generate("pictdkfwm101.jpg", bandwidth= '3g')
    else:
        h.generate("pictdkfwm101.jpg",size=320)
    end = time.time()
    print('Timetaken for {} is {}'.format(ind, end-start))

print('Printing for {} items took {} ticks'.format(items, time.time()-tim1))