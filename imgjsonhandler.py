import time
import json
import logging.handlers
import logging
from imgprocessor import imgprocessor

class imgjsonhandler(object):

    '''Initialize the logger to log information'''
    #mylogger = logging.getLogger('JsonImageHandler')
    #handler = logging.handlers.RotatingFileHandler('jsonimage.log', 'a', maxBytes=10000000, backupCount=5)
    #mylogger.addHandler(handler)

    def outputjson(self,filename,size,bandwidth,returnfullpath):
        try:
            jsondata = json.dumps({})
            print('processing for {}, {}, {}'.format(filename,size,bandwidth))
            imgname = imgprocessor.generate(filename,size,bandwidth,returnfullpath)
            print('processed')
            data = {"path": imgname, "key": "{}_{}_{}".format(filename,size,bandwidth)}
            #self.mylogger.log(data)
            jsondata = json.dumps(data)
        except Exception as ex:
            print(ex)
            #self.mylogger.exception(msg='Exception occurred in image generation for {}'.format(filename), exc_info=ex)
        finally:
            #self.mylogger.info(msg="Processing for {} completed, check log for any errors.".format(filename))
            return jsondata


if __name__ == '__main__':
    imgjson = imgjsonhandler()
    '''Handle or get the values here from the request handler and set the same'''
    values = ['nasa.jpeg', 320, '2g', False]

    '''the output automatically will be of json with content type and values set
    the output would have 2 keys.
    path = imagename & key = unique key for the image & screen, size combination to handle in edge servers like varnish
    '''
    print('content-type:application/json')
    print(imgjson.outputjson(values[0],values[1],values[2],values[3]))