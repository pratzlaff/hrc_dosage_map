import astropy.io.fits
import numpy as np
import os

def fits_img_mean(fname):
    with astropy.io.fits.open(fname) as hdul:
        return np.mean(hdul[0].data)

#--------------------------------------------------------------------------
#-- read_data_file: read a data file and create a data list              --
#--------------------------------------------------------------------------

def read_data_file(ifile, remove=0, ctype='r'):
    """
    read a data file and create a data list
    input:  ifile   --- input file name
            remove  --- if > 0, remove the file after reading it
            ctype   --- reading type such as 'r' or 'b'
    output: data    --- a list of data
    """
#
#--- if a file specified does not exist, return an empty list
#
    if not os.path.isfile(ifile):
        return []

    try:
        with open(ifile, ctype) as f:
            data = [line.strip() for line in f.readlines()]
    except:
        with codecs.open(ifile, ctype, encoding='utf-8', errors='ignore') as f:
            data = [line.strip() for line in f.readlines()]
#
#--- if asked, remove the file after reading it
#
    if remove > 0:
        os.unlink(ifile)

    return data
