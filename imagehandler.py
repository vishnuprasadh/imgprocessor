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

    '''Default screensize, band will be set once initialized'''
    defaultscreen = {}
    defaultband = {}

    '''The root path for all images'''
    imagepath = {}
    sumup=0
    '''This will be used to resize and set quality of image'''
    qualityscore =60
    qualityconfig = {}
    qualityvalues =dict()
    scales = dict()

    '''Initialize the logger to log information'''
    mylogger = logging.getLogger('Imagehandler')
    handler = logging.handlers.RotatingFileHandler('imghandler.log','a',maxBytes=10000000,backupCount=5)
    mylogger.addHandler(handler)

    def generate(self,filename,ssize="1080",band="*"):

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
            qualityconfig = config.get(section="config",option="qualityscore")
            scaleconfig = config.get(section="config",option="scale")
            defaultscreen = config.get(section="config",option="defaultscreen")
            defaultband = config.get(section="config",option="defaultbandwidth")
            imagepath = config.get(section="config",option="path")
            screens = dict(screenmix.split(",")  for screenmix in screenconfig.split(";"))
            bandwidth = dict(band.split(",") for band in bandconfig.split(";"))
            self.qualityvalues = dict(quality.split(",") for quality in qualityconfig.split(";"))
            self.scales = dict(scale.split(",") for scale in scaleconfig.split(";"))
            self.mylogger.info(msg="Done initialization")

            imgfile = BytesIO()
            self.mylogger.info('Generating file {}'.format(filename))
            '''Expected name of the file to be generated'''
            scale = self._getoptimizesizebasedonsizebandwidth(ssize, band, screens, bandwidth)
            #print("Scale is {}".format(scale))
            savefilename = filename.split(".")[0] + "_" + str(self.sumup) + "." + filename.split(".")[1]
            savefilename = os.path.join(imagepath, savefilename )

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
                if not os.path.isfile(fullpath):
                    raise NameError('File not found')

                '''if fullpath is file, then open the same'''
                img = Image.open(fullpath, 'r')
                self.mylogger.info("Size of image is {}".format(img.size))
                img.thumbnail((int(img.size[0]* float(scale)) , int(img.size[1]*float(scale))),Image.LANCZOS)
                '''saved locally'''
                #img.save(savefilename,format="JPEG")
                '''load from bytes too'''
                img.save(imgfile,format="JPEG",quality= int(self.qualityscore) )
                '''encode it using base64 and return in asciformat'''
                #base64encode = base64.encodebytes(imgfile.getvalue())
                #return base64encode.decode('ascii')
                return imgfile.getvalue()


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
        self.sumup = float(size) + float(band)
        #print(self.sumup)
        self.mylogger.info('Sumup value is {}'.format(self.sumup))
        if float(self.sumup) <= 4:
            self.sumup = 4
            self.qualityscore = self.qualityvalues.get("4")
            return self.scales.get("4")
        elif float(self.sumup) <= 7:
            '''I am sure screen is of medium size and bandwidth is around 2g'''
            self.sumup = 7
            self.qualityscore = self.qualityvalues.get("7")
            return self.scales.get("7")
        elif float(self.sumup) <=10:
            '''I know this is of medium resolution and high bandwidth or high res with low bandwidth'''
            self.sumup = 10
            self.qualityscore = self.qualityvalues.get("10")
            return self.scales.get("10")
        else:
            '''I am sure if the value is > 4, its either 3g, 4g etc with higher screensize'''
            self.sumup = 11
            self.qualityscore = self.qualityvalues.get("*")
            return self.scales.get("*")



if __name__ == '__main__':
    '''Handle or get the values here from the request handler and set the same'''
    '''Replace this with input from handler'''
    import cgi
    formdata = cgi.FieldStorage()
    filename=""
    size=""
    band=""
    if formdata.length <= 0:
        filename = "nasa.jpeg"
        size= '720'
        band='2g'
    else:
        filename=""

    '''the output automatically will be of json with content type and values set
    the output would have 2 keys.
    path is imagename & key is unique key for the image & screen, size combination to handle in edge servers like varnish
    '''
    print('content-type:image/jpg\n')
    img  = imagehandler()

    header = StringIO()
    header.write('key:')
    header.write(filename)
    header.write("_")
    header.write(size)
    header.write("_")
    header.write(band)
    header.write("\n")

    print(header.getvalue() )
    i = img.generate(filename,size,band)
    print(i)