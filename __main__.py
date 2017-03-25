import imgprocessor
import argparse

def _launch():
    args = argparse.ArgumentParser(prog='python -m imgprocessor',
                               description='Given a filename with screensize, bandwidth the program generates the file and provides the output of the filepath with name',
                               add_help='provide filename as firstparameter, screen w=width e.g. 720 or 1024 etc, bandwidth as third parameter i.e. 2g,3g,4g or * in case of default'
                               )
    args.add_argument('--f','--file',action='store_true')
    args.add_argument('-s','--size',action='store_true',default=740)
    args.add_argument('-b','--bandwidth',action='store_true',default='3g')
    args.add_argument('-r','--returnpath',action='store_true',default=False)

    args = args.parse_args()
    imgprocess = imgprocessor()
    imgprocess.generate(args.file,args.size,args.bandwidth,args.returnpath)

if __name__== '__main__':
    _launch()