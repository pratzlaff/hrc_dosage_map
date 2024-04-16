#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       mta_convert_fits_to_image.py: convert a fits img file to a ps, gif, jpg, or png file    #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                               #
#       last update: Jan 27, 2021                                                               #
#                                                                                               #
#################################################################################################

import glob
import os
import re
import string
import subprocess
import sys
import time

import HRCExp

#----------------------------------------------------------------------------------------
#-- mta_convert_fits_to_image: convert a fits img file to a ps, gif, jpg, or png file ---
#----------------------------------------------------------------------------------------

def mta_convert_fits_to_image(infile, outfile, scale='log', \
                              size = '125x125', color='heat', itype='png'):
    """
    convert a fits img file to a ps, gif, jpg, or png file 
    input:  infile  --- input fits file name
            outfile --- output png file name without a suffix
            scale   --- scale of the output image; log, linear, or power
            size    --- size of the output image; format: 125x125 
                            --- no contorl of size on ps and jpg file
            color   --- color of the output image: hear, rainbow1 etc. default is grey
                        to see which color is available, 
                        type: 'ls /home/ascds/DS.release/data/*.lut'
            itype    --- image type: ps, gif, jpg, or png
    output: outfile
    """
#
#--- set scale
#
    scale = scale.lower()
    if scale not in ('log', 'power'):
        scale = 'linear'
#
#--- set default size
#
    if size == '' or size == '-':
        size = '125x125'
#
#--- read color list
#
    color_list = [ re.search(r'(\w+).lut', f).groups()[0]
                    for f in glob.glob(f'{os.environ["ASCDS_CALIB"]}/*.lut')]

#
#--- make sure the color specified is in the list, if not, assign grey
#
    if not (color in color_list):
        color = 'grey'
#
#--- set output format
#
    itype = itype.lower()
    if itype not in ('ps', 'gif', 'jpg', 'png'):
        itype = 'gif'
#
#--- define output file name
#
    outfile = outfile + '.' + itype
#
#--- convert a fits image into an eps image
#
    dmimg2jpg_args = ['dmimg2jpg',
                      infile, 
                      'greenfile=',
                      'bluefile=',
                      'regionfile=',
                      'outfile=foo.jpg',
                      f'scalefunction={scale}',
                      'psfile=foo.ps',
                      f'lut=)lut.{color}',
                      'showgrid=no',
                      'cl+'
                      ]
    subprocess.run(dmimg2jpg_args)

#
#--- convert and move the image to the correct format and file name
#
    if itype in ('ps', 'jpg'):
        shutil.move(f'foo.{itype}', outfile)

    elif itype == 'gif':
        cmd = 'echo ""|gs -sDEVICE=ppmraw  -r' + size 
        cmd = cmd + '  -q -dNOPAUSE -sOutputFile=-  ./foo.ps |' 
        cmd = cmd + 'ppmtogif > ' + outfile
        os.system(cmd)

    elif itype == 'png':
        cmd = 'echo ""|gs -sDEVICE=ppmraw  -r' + size 
        cmd = cmd + '  -q -dNOPAUSE -sOutputFile=-  ./foo.ps |' 
        cmd = cmd +  'pnmtopng > ' + outfile

        os.system(cmd)

    try:
        [ os.unlink(f) for f in glob.glob('foo.*') ]
    except:
        pass

#--------------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) < 3:
        infile = '/data/mta_www/mta_max_exp/Cumulative/ACIS_07_1999_04_2012_s3.fits.gz'
        outfile='test'
        scale  = 'log'
        size   = '125x125'
        color  = 'heat'
        itype  = 'png'
    else:
        infile  = sys.argv[1]
        outfile = sys.argv[2]
        scale  = 'log'
        size   = '125x125'
        color  = 'heat'
        itype  = 'png'

    mta_convert_fits_to_image(infile, outfile, scale, size, color, itype)


