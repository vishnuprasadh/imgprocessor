DYNAMIC IMAGE CONVERTOR

PURPOSE
Given a Image filename with screensize, bandwidth the program generates the image file and provides the output of the filepath with name.

Primary intent of this program is to embed this as part of apache log to generate and ouput image files dynamically

Provide filename of image as firstparameter, screen w=width e.g. 720 or 1024 etc, bandwidth as third parameter i.e. 2g,3g,4g or * in case of default and full folder image path = True in case you are sending full physicalpath and expecting the fullpath back else false

DEPENDENCY
Run setup.py to ensure your dependencies are installed. The key dependencies are:
```bash
pip install Pillow-simd
pip install numpy
pip install logging
pip install configparser
pip install setuptools
```
INSTALL
Python2
```bash
sudo python setup.py install 
```
Python3
```
python3 setup.py install
```

RUN TOOLS
Option A: CommandLine
```python
python imgprocessor 'nasa.jpeg' 720 2g
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

