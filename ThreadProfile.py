from urllib.request import Request,urlopen
import urllib.response
import numpy as np
import random
import time
import pandas as pd
from threading import Thread
from time import sleep

nw_type = ['2g','3g','4g','*']
#http://10.129.34.55:8051/images/?name=nasa.jpeg&width={}&height={}
url = "http://groc-example.com:8051/images/?name=nasa.jpeg&&width={}&height={}"

class imagedownloader(Thread):
    lists = list()
    imagecount = 0
    #name = ""

    def __init__(self,lists,imagecounts=10):
        Thread.__init__(self)
        self.lists = lists
        self.imagecount=imagecounts
        #self.name =  "Thread-{}".format(np.random.randint(10,100))

    def downloadimage(self):
        print("Started thread")
        try:
            for index in range (1,self.imagecount):
                w = np.random.randint(low=100,high=700)
                h = np.random.randint(low=200,high=500)
                nwtype = str(random.choice(nw_type)).capitalize()

                start = time.time()
                req =  Request( url.format(w,h))
                req.add_header("nw_type",nwtype)
                output = urlopen(req)

                end = time.time()

                #print("Image {} rendered for {} x {} of size {} ".format(output.headers['imagekey'], w,h, str(output.headers['Content-Length'])))
                #print("Time to process is {}".format( str(end - start)))

                lists.append({'image':output.headers['imagekey'], 'width':w ,'height': h, 'size(bytes)': output.headers['Content-Length'],
                              'time(sec)':str(end-start),'timstamp':str(end)})
                #lists.append({output.headers['imagekey'],  w, h,output.headers['Content-Length'], str(end - start)})
                #print("thread name is {}".format(self.name))

        except Exception as ex:
            print(ex)
        finally:
            print("thread name is {}".format(self.name))
            return lists



if __name__ == '__main__':
    lists =list()
    #when using threads
    threads = []
    df = []
    for i in range(25):
        worker = imagedownloader(lists,30)
        worker.daemon = True
        lists = worker.downloadimage()
        #worker.start()
        threads.append(worker)

    for th in threads:
        th.start()

    df = pd.DataFrame(lists)
    with open('imageoutput.csv','a') as f:
        df.to_csv(f,sep=',',mode="a")
    print(df)
    print("Process completed")
