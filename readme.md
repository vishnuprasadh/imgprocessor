DYNAMIC IMAGE CONVERTOR

PURPOSE

Given a Image filename with screensize, bandwidth the program generates the image file and provides the output of the filepath with name or the output of resized image as Bytes or renders the entire image as bytes for a given url passed.

Primary intent of this program is to embed this as part of apache log to generate and ouput image files dynamically. It also provides capability to resize image when WXH is passed in querystring with option to forcefit the size and return or return the best fit option with no aspect ratio loss.


The program supports option to configure runenvironment in multiple mode:
1 Standalone mode - Using mod_wsgi-express start-server wsgiimagehandler.py --options command you can run the program in standalone imgae servermode.
2. Updating the httpd.conf and httpd-vhosts.conf for virtualhost entry or run as independant handler for apache requests.
3. Mixed mode : Combination of 1 and 2 where you run wsgiimagehandler in mod_wsgi and for all other requests use apache httpd.conf. 

In addition you can very easily create an nginx or varnish front end to cache/edge cache enable the outcomes.

Program can be run as commandline to just get output file or JSON handler to get path of image or Imagehandler to output content as image in bytes.

Primary case used is Imagehandler using wsgiimagehandler.py:
http://groc-images.com/images/name=vegetables.jpg&width=500&height=200&fsize=1
QueryString: Provide filename of image as firstparameter, width of screen as second param, height as third. fsize actually force sizes the input WXH when given as 1 which means your aspect ratio is lost. Default is no aspect ratio loss. All these params outside of name of file are optional.

Header values:
SCREENWIDTH i.e. only width e.g. 720 or 1024 etc and NW_TYPE i.e. bandwidth as third parameter i.e. 2g,3g,4g or * in case of default.

Secondary case of Imagehandler through modules of imgjsonhandler or cmdimgprocessor.
'--file', required=True, help='The name of image file to generate')
'--size' ,required=False, default=740 ,help='The size of client device, defaults to 740')
'-b', '--bandwidth',required=False, default='*' ,help='The bandwidth of device, defaults to high bandwidth.You can give 2g,3g,4g or *')
'-r', '--returnpath',required=False, default=False, help='If you need full returnpath provide true here' )

Note that in this case parameters of WXH, fsize which was available in Imagehandler is not yet supported.

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

