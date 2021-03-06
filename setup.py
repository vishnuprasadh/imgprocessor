from setuptools import setup

setup(name="imgprocessor",
    description='Dynamically generates runtime image file resized based on bandwidth, screensize',
    author='vishnu prasad hari',
    author_email='vishnuprasadh@gmail.com',
    keywords='Pillow-SIMD,PIP,Dynamic image rendering,dynamicimage,Image rendering',
    license='MIT',
    py_modules=['imgprocessor','imagehandler','imgjsonhandler','wsgiimagegenerator','wsgiimagehandler'],
    version='0.1',
    download_url='https://github.com/vishnuprasadh/imgprocessor.git',
    url='https://github.com/vishnuprasadh/imgprocessor',
    install_requires=['Pillow-SIMD','configparser','setuptools','mod_wsgi','logging'],
    exclude_package_data={'':['README.MD'],'':['README.TXT'],'':['Config.cfg']}
    )
