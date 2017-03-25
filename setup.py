from setuptools import setup

setup(name="DIG", description='Dynamically generates runtime image file resized based on bandwidth, screensize',
      author='vishnu prasad hari',
      author_email='vishnuprasadh@gmail.com',
      keywords='Pillow-SIMD,PIP,Dynamic image rendering,dynamicimage,Image rendering',
      license='MIT',
      py_modules=['imgprocessor'],
      version='0.1',
      install_requires=['Pillow-SIMD','numpy','configparser','setuptools'],
      zip_flag=False)
