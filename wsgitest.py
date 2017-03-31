from wsgiref.simple_server import make_server
from wsgiref.handlers import CGIHandler
import io
from mod_wsgi import server
from imagehandler import imagehandler
import cgi

def application(environment,start_response):
    response = "Oops, we are sorry!"
    status = "200 OK"

    '''Parse querystring tp get the values'''
    params = cgi.parse_qs(environment["QUERY_STRING"])

    '''initialize the key variables we would be using for passing imagegenerator'''
    filename = ""
    screensize = ""
    bwidth = ""

    '''resolve imagename in querystring'''
    if any(params):
        filename = params.get("name")[0]


    if environment.get("HTTP_NW_TYPE") == 'NoneType':
        bwidth = "2g"
    else:
        bwidth = environment.get("HTTP_NW_TYPE")

    if environment.get("HTTP_SCREENSIZE") == 'NoneType':
        screensize = "320"
    else:
        screensize = environment.get("HTTP_SCREENSIZE")

    if environment["PATH_INFO"] == '/images/':
        img = imagehandler()
        response = img.generate(filename,screensize,bwidth)
        #with open(filepath,'r') as f:
        #    response = f.read()
        #   f.close()
        #response ="Hello world"

    resQueryString = "{}_{}_{}".format(filename,screensize,bwidth)

    responseheaders = [("Content-Type", "image/jpeg"),
                       #("Content-Type","text/html"),
                       ("Content-Length", str(len(response))),
                       ("Server","Encrypt"),
                       ("imagekey", resQueryString)]




    start_response(status,responseheaders)
    return [response]

httpd = make_server('',8052,application)
httpd.serve_forever()