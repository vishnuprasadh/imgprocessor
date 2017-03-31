DYNAMIC IMAGE CONVERTOR

PURPOSE
Given a Image filename with screensize, bandwidth the program generates the image file and provides the output of the filepath with name or the output of resized image as Bytes or renders the entire image as bytes for a given url passed.

Primary intent of this program is to embed this as part of apache log to generate and ouput image files dynamically. It supports option to configure specific runscripts in httpd-vhosts.conf for virtualhost entry or run as mod_wsgi program or also as commandline or batch scripts.

Input this takes:
Provide filename of image as firstparameter, screen width i.e. only width e.g. 720 or 1024 etc and bandwidth as third parameter i.e. 2g,3g,4g or * in case of default and full folder image path = True in case you are sending full physicalpath and expecting the fullpath back else false. You can ignore this for majority of case.

PYTHON FILES
1. imgprocessor
The file which actually generates resized thumbnails based on screensize, bandwidth saves it as per the root configuration path in config file and returns the file path.
2. imagehandler
The file which does very similar to imgprocessor excecpt that instead of saving it locally, it returns the Byte of the image which can directly be applied to <img src="data:XXX"/> or just output as images.
3. imgjsonhandler
This internally uses imgprocessor and returns the output as json. You can wrap this with Content-Type:application/json and render it to frontend or directly call from ajax, parse and use it.
4. wsgiimagehandler
As the name suggests this is a wsgi program which runs on 8051 port and returns image data i.e. content-type:image/jpeg.Internally this uses imagehandler to get the bytes and render back. This looks for 3 key parameters as input with following constraints:
a. /image/ pattern in url
b. filename as querystring to find the name of the jpeg. In case you want to pass full path name then in config file set path: i.e. empty path: set.
c. it looks for keys in httpheader in the request which are screensize and nw_type. Screensize can be 320,360,480,540,5;1080,720,640,240 and the network can be 2g,3g,4g or blank.
If both screensize and network is not passed, the system assumes 320 as screen and 2g as network to give the most optimal output.

DEPENDENCY 

Run setup.py to ensure your dependencies are installed. The key dependencies are:
```bash
pip install Pillow-SIMD
pip install logging
pip install configparser
pip install setuptools
pip install mod_wsgi
```
Post above, goto httpd.conf in apache and enable for mod_cgi.so and also uncomment loadmodule for httpd-vhosts in case of virtualhost configuration.

TIP: Use this library with media asset randomization for max.benefit.

INSTALL
Do not run installer in case you want to use this as mod_wsgi python script with apache for imagehandling. Instead copy the files into folder and run the pip commands given in dependency section(sudo access may be required) and then standalone python comamnd as given in section 3
Section 1: Python2 - Install as libraries and then run it as batch or standalone app

```bash
sudo python setup.py install 
```
Section 2: Python3- Install as libraries and then run it as batch or standalone app

```bash
python3 setup.py install
```
Section 3: Modcgi Mode
```bash
python wsgiimagehandler.py
```
RUN TOOLS

Option A: CommandLine

```python
python imgprocessor 'nasa.jpeg' 720 '2g'
```
Option B: Import

```python
import imgprocessor
def gen():
  img = imgprocessor()
  img.generate('nasa.jpeg',720,'2g')
```


USAGE

You can either run this as a standalone python command by executing python commandline or hook this up with apache to dynamically render
and return the images. you can also import imgprocessor and call generate method

