import argparse
from imgprocessor import imgprocessor

'''the program is used only for commandline execution'''
args = argparse.ArgumentParser(prog='python -m imgprocessor',
                               description='Given a filename with screensize, bandwidth the program generates the file and provides the output of the filepath with name',
                               add_help='provide filename as firstparameter, screen w=width e.g. 720 or 1024 etc, bandwidth as third parameter i.e. 2g,3g,4g or * in case of default'
                               )
args.add_argument('-f', '--file', required=True, help='The name of image file to generate')
args.add_argument('-s', '--size' ,required=False, default=740 ,help='The size of client device, defaults to 740')
args.add_argument('-b', '--bandwidth',required=False, default='*' ,help='The bandwidth of device, defaults to high bandwidth.You can give 2g,3g,4g or *')
args.add_argument('-r', '--returnpath',required=False, default=False, help='If you need full returnpath provide true here' )


'''We need this to enable commandline capabilities'''
if __name__ == '__main__':
    pargs = argparse.Namespace()
    pargs = args.parse_args()
    if not pargs == None:
        img = imgprocessor()
        img.generate(pargs.file, pargs.size, pargs.bandwidth, pargs.returnpath)


