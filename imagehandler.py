#!/usr/bin/env python
import os
import time
import sys
import logging.handlers
import logging
import base64
from PIL import Image
from PIL import ImageFilter
from PIL import  ImageEnhance
from configparser import ConfigParser
from configparser import ExtendedInterpolation
from pkg_resources import resource_stream, Requirement
from io import BytesIO
from  io import StringIO


class imagehandler(object):
    '''the class is used for processing of the image dynamically and accepts the name of the original image
    the screensize and the bandwidth. This provides a byte image output
    Based on these values, the program will do simple logic of sending the most optimal  image as ByteArray.
    THis may need conversin to Base64 if someone intends to leverage as string
    the optimal PIL-SIMD based Image generation which is faster than most other tools including Imagemagica by approx 10-15times
    '''
    '''All configured bandwidth, screens will be initialized with a weightage'''
    bandwidth = dict()
    screens = dict()
    dynamicqualityvalues =dict()
    bandqualityvalues = dict()
    scales = dict()

    '''Default screensize, band will be set once initialized'''
    defaultscreen = {}
    defaultband = {}

    '''The root path for all images'''
    imagepath = {}
    sumup=0

    '''This will be used to resize and set quality of image'''
    qualityscore =60



    '''Initialize the logger to log information'''
    mylogger = logging.getLogger('Imagehandler')
    handler = logging.handlers.RotatingFileHandler('imghandler.log','a',maxBytes=10000000,backupCount=5)
    mylogger.addHandler(handler)

    iswidthheightset = False

    '''
    This method Generates an output of byte of an image
    filename - provide the path to the file. The core mount path is configured in configuration. This config property and the filename
    value given here will be joined to get a fullpath or real path
    screensize - in case we are sending screensize parameter. if width and height of image is sent then this property becomes irrelevant
    band - is the bandwidth or network type. This can be 2g,3g,4g or *. This will be used purely to optimize quality of image and hence size
    width - the image width
    height - the image height which is required.
    '''
    def generate(self,filename,ssize="1080",band="*",width=0,height=0):

        try:

            '''To avoid issues with zerolength params, default such items'''
            if ssize == "None" or len(str(ssize))==0 : ssize = "1080"
            if  band == "None" or len(str(band))==0 :band="*"

            '''if weight is given but height not given or other way around'''
            width = int(width)
            height = int(height)

            #if (width >0 and height==0) : height = width
            #if (height>0 and width==0): width = height

            self.mylogger.info(msg="Starttime is {}".format(time.time()))
            config = ConfigParser()
            config._interpolation = ExtendedInterpolation()

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
            dynamicqualityconfig = config.get(section="config",option="dynamicqualityscore")
            bandqualityconfig = config.get(section="config",option="bandqualityscore")
            scaleconfig = config.get(section="config",option="scale")
            defaultscreen = config.get(section="config",option="defaultscreen")
            defaultband = config.get(section="config",option="defaultbandwidth")


            imagepath = config.get(section="config",option="path")
            '''Populate all the dict values from configuration'''
            self.screens = dict(screenmix.split(",")  for screenmix in screenconfig.split(";"))
            self.bandwidth = dict(band.split(",") for band in bandconfig.split(";"))
            self.dynamicqualityvalues = dict(quality.split(",") for quality in dynamicqualityconfig.split(";"))
            self.bandqualityvalues = dict(quality.split(",") for quality in bandqualityconfig.split(";"))
            self.scales = dict(scale.split(",") for scale in scaleconfig.split(";"))

            if (width >0 and height >0): self.iswidthheightset = True
            self.mylogger.info(msg="Done initialization")

            imgfile = BytesIO()
            self.mylogger.info('Generating file {}'.format(filename))
            '''Expected name of the file to be generated'''
            #scale = self._getoptimizesizebasedonsizebandwidth(ssize, band, screens, bandwidth)
            #savefilename = filename.split(".")[0] + "_" + str(self.sumup) + "." + filename.split(".")[1]

            '''A consistent logic is used to generate name of image'''
            savefilename = self._createimageid(filename.split(".")[0],ssize,band,width,height) + filename.split(".")[1]

            savefilename = os.path.join(imagepath, savefilename )

            #print(savefilename)

            '''if filealready exist return file name'''
            if os.path.isfile(savefilename):
                img = Image.open(savefilename)
                img.save(imgfile,format="JPEG")
                '''encode it using base64 and return in asciformat'''
                #base64encode=  base64.encodebytes(imgfile.getvalue())
                #return base64encode.decode("ascii")
                return imgfile.getvalue()
            else:
                '''Open the file if it isnt there and resize, send back the path'''
                '''Check if input fullpath leads to file, if not throw exception'''
                fullpath = os.path.join(imagepath, filename)
                #print(fullpath)
                if not os.path.isfile(fullpath):
                    raise NameError('File not found')

                '''if fullpath is file, then open the same'''
                img = self._getimage(fullpath,ssize,band,width,height)
                '''load from bytes too'''

                '''Sharpen by 1.5, detail out and set subsampling to 0'''
                sharp = ImageEnhance.Sharpness(img)
                img = sharp.enhance(1.5)
                img = img.filter(ImageFilter.DETAIL)
                img.save(imgfile, format="JPEG" ,subsampling=0, quality=int(self.qualityscore))

                '''encode it using base64 and return in asciformat'''
                #base64encode = base64.encodebytes(imgfile.getvalue())
                #return base64encode.decode('ascii')
                return imgfile.getvalue()


            self.mylogger.info("Saved file {} for {}".format(filename,savefilename))
        except NameError as filenotfound:
            raise NameError('File {} doesnt exist. Exception - {}'.format(filename,str(filenotfound)))
            self.mylogger.exception("Exception occurred in image generation for {}".format(filename))
        finally:
            self.mylogger.info("Completed")

    '''Creates a consistent naming for file given the options available'''
    def _createimageid(self,filename,ssize,band,width,height):
        if self.iswidthheightset:
            filename = "{}_{}x{}_{}".format(filename,width,height,band)
        else:
            self._calculatescreenandbandscore(ssize,band)
            filename = "{}_{}".format(filename,self.sumup)
        #print (filename)
        return filename

    def _getimage(self,fullpath, size,band,width,height):
        img = Image.open(fullpath, 'r')
        self.mylogger.info("Size of image is {}".format(img.size))

        if self.iswidthheightset:
            self._resolvequality(band)
            #print(self.qualityscore)
            #enhance = ImageEnhance.
            img.thumbnail((int(width), int(height)),Image.LANCZOS)
        else:
            scale = self._resolvequalityandscale()
            #print(self.qualityscore)
            img.thumbnail((int(img.size[0] * float(scale)), int(img.size[1] * float(scale))), Image.LANCZOS)
        '''saved locally'''
        # img.save(savefil  ename,format="JPEG")
        return img

    '''We will set the optimized value for image generation based on size & bandwidth'''
    def _calculatescreenandbandscore(self,size,band):
        '''If the sizeinfo is not configured, send the highest sizeinfo available'''
        self.mylogger.info(msg='Size & bandwidth is {} & {}'.format(size,band))
        #print(self.screens)
        try:
            size = self.screens[str(size)]
        except Exception:
            size = max({val:key for key, val in self.screens.items()})
            #mylogger.info('Size was not found and defaulting to size {}'.format(size))
        '''if input value isnt configured, send the highest bandwidth configured'''
        try:
            band = self.bandwidth[band.lower()]
        except Exception:
            band =  max({val:key for key, val in self.bandwidth.items()})
            #mylogger.info('Bandwidth was not found and defaulting to size {}'.format(bandwidth))
        #print(self.sumup)
        self.sumup = int(size) + int(band)
        self.mylogger.info('Sumup value is {}'.format(self.sumup))



    '''Based on the network type and screensize the application itself does some approx scaling and returns the scale factor'''
    def _resolvequalityandscale(self):
        if float(self.sumup) <= 4:
            self.sumup = 4
            self.qualityscore = self.dynamicqualityvalues.get("4")
            return self.scales.get("4")
        elif float(self.sumup) <= 7:
            '''I am sure screen is of medium size and bandwidth is around 2g'''
            self.sumup = 7
            self.qualityscore = self.dynamicqualityvalues.get("7")
            return self.scales.get("7")
        elif float(self.sumup) <=10:
            '''I know this is of medium resolution and high bandwidth or high res with low bandwidth'''
            self.sumup = 10
            self.qualityscore = self.dynamicqualityvalues.get("10")
            return self.scales.get("10")
        else:
            '''I am sure if the value is > 4, its either 3g, 4g etc with higher screensize'''
            self.sumup = 11
            self.qualityscore = self.dynamicqualityvalues.get("*")
            return self.scales.get("*")


    '''Resolves only quality setting here and not the screensize of requesting. Use this when we know absolute sizeof image to resize
    but need to set the quality of image depending on network being used'''
    def _resolvequality(self,band):
        try:
            band = self.bandwidth[band.lower()]
        except Exception:
            band = max({val: key for key, val in selfbicu.bandwidth.items()})
            # mylogger.info('Bandwidth was not found and defaulting to size {}'.format(bandwidth))
        self.sumup = int(band)
        if float(self.sumup) <= 1:
            '''I am sure this is  2g'''
            self.qualityscore = self.bandqualityvalues.get("1")
        elif float(self.sumup) < 3:
            self.qualityscore = self.bandqualityvalues.get("2")
        elif float(self.sumup) < 5:
            self.qualityscore = self.bandqualityvalues.get("3")
        else:
            self.qualityscore = self.bandqualityvalues.get("*")




if __name__ == '__main__':
    '''Handle or get the values here from the request handler and set the same'''
    '''Replace this with input from handler'''
    import cgi
    formdata = cgi.FieldStorage()
    filename=""
    size=""
    band=""
    width ="0"
    height = "0"
    if formdata.length <= 0:
        filename = "nasa.jpeg"
        width = "200"
        height = "300"
        #size= '720'
        #band='*'

    else:
        filename=""

    '''the output automatically will be of json with content type and values set
    the output would have 2 keys.
    path is imagename & key is unique key for the image & screen, size combination to handle in edge servers like varnish
    '''
    print('content-type:image/jpg\n')
    img  = imagehandler()

    #i = img.generate(filename,size,band)
    i = img.generate(filename, ssize=size,band= band,width=width ,height=height)
    print(i)