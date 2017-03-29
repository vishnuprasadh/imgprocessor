#! /usr/bin/env python
import time
import json
import logging.handlers
import logging
from imgprocessor import imgprocessor


class imgjsonhandler(object):


    '''This can be used in Django or CGI gateway for making calls and getting JSON while generating the image locally'''
    '''Initialize the logger to log information'''
    mylogger = logging.getLogger('jsonimagehandler')
    handler = logging.handlers.RotatingFileHandler('jsonimagehandler.log', 'a', maxBytes=10000000, backupCount=5)
    mylogger.addHandler(handler)

    def outputjson(self,filename,size,bandwidth,returnfullpath):

        try:
            imgprocess = imgprocessor()
            jsondata = json.dumps({})
            self.mylogger.info('processing for {}, {}, {}'.format(filename,size,bandwidth))
            imgname = imgprocess.generate(filename=filename,size=size,bandwidth=bandwidth,returnFullpath=returnfullpath)
            self.mylogger.info('processed')
            data = {"path": imgname, "key": "{}_{}_{}".format(filename,size,bandwidth)}
            jsondata = json.dumps(data)
        except Exception as ex:
            self.mylogger.exception(ex)
        finally:
            return jsondata


if __name__ == '__main__':
    imgjson = imgjsonhandler()

    '''Handle or get the values here from the request handler and set the same'''
    '''Replace this with input from handler'''
    filename = "nasa.jpeg"
    size= 720
    band='2g'
    returnfullpath = False

    '''the output automatically will be of json with content type and values set
    the output would have 2 keys.
    path is imagename & key is unique key for the image & screen, size combination to handle in edge servers like varnish
    '''
    print('content-type:application/json')
    output = imgjson.outputjson(filename,size=size,bandwidth=band, returnfullpath=returnfullpath)
    print(output)