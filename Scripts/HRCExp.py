import astropy.io.fits
import numpy as np
import os
import shutil

def fits_read_raw(fname):
    """Return RAW coordinates from an events list, status-filtered for
    HRC.
    """
    with astropy.io.fits.open(fname) as hdulist:
        status = hdulist['events'].data.status
        rawx = hdulist['events'].data.rawx
        rawy = hdulist['events'].data.rawy
    mask = status_mask(status)
    return rawx[mask], rawy[mask]

def raw_hist(rawx, rawy, x0, x1, y0, y1):
    """Return RAW coordinates 2d histogram, with single-pixel
    binning.
    """
    mask = (rawx >= x0) & (rawx <= x1) & (rawy >= y0) & (rawy <= y1)
    nx = x1-x0+1
    ny = y1-y0+1
    h, yedge, xedge = np.histogram2d(rawy[mask], rawx[mask], bins=(ny, nx), range=[[y0-0.5,y1+0.5],[x0-0.5,x1+0.5]])
    return h

def fits_img_hist(fname):
    with astropy.io.fits.open(fname) as hdul:
        img = hdul[0].data
        dmax = img.max()
        hist, bin_edges = np.histogram(hdul[0].data, bins=dmax, range=(0.5, dmax+0.5))
        return hist, bin_edges

def fits_img_hist(fname):
    with astropy.io.fits.open(fname) as hdul:
        img = hdul[0].data
        dmax = img.max()
        hist, bin_edges = np.histogram(hdul[0].data, bins=dmax, range=(0.5, dmax+0.5))
        return hist, bin_edges

def fits_img_add_inplace(if1, if2):
    with astropy.io.fits.open(if1) as hdul1:
        with astropy.io.fits.open(if2, mode='update') as hdul2:
            hdul2[0].data += hdul1[0].data

def fits_img_add(if1, if2, of):
    shutil.copyfile(if1, of)
    fits_img_add_inplace(if2, of)

def status_mask(status):
    """Return mask for status-filtered events."""
    status_zeros = [6,7,17,18,19,21,22,23,26,27]
    mask = (status[:,status_zeros[0]] == False)
    for i in range(1, len(status_zeros)):
        mask = mask & (status[:,status_zeros[i]] == False)
    return mask

def fits_img_mean(fname):
    with astropy.io.fits.open(fname) as hdul:
        return np.mean(hdul[0].data)

def stats(fname):
    with astropy.io.fits.open(fname) as hdul:
        image = hdul[0].data
        hdr = hdul[0].header
        image[image<0] = 0
        image[image>1e10] = 0
        mean = image.mean()
        dev = image.std()
        minx, miny = np.unravel_index(np.argmin(image), image.shape)
        maxx, maxy = np.unravel_index(np.argmax(image), image.shape)
        dmin = image[minx, miny]
        dmax = image[maxx, maxy]
        minx += hdr['CRVAL2P']+0.5
        maxx += hdr['CRVAL2P']+0.5
        miny += hdr['CRVAL1P']+0.5
        maxy += hdr['CRVAL1P']+0.5
        return mean,  dev,  dmin,  dmax , miny,  minx,  maxy,  maxx

def hdu_add_img_wcs(hdu, refrawx, refrawy):
    hdr = hdu.header
    hdr['ACSYS1'] = 'RAW:AXAF-HRC-1.1'
    hdr['MTYPE1'] = 'raw'
    hdr['MFORM1'] = 'rawx,rawy'

    hdr['CTYPE1P'] = 'rawx'
    hdr['CRVAL1P'] = refrawx-0.5
    hdr['CRPIX1P'] = 0.5
    hdr['CDELT1P'] = 1.0

    hdr['WCSTY1P'] = 'PHYSICAL'
    hdr['LTV1'] = -refrawx+1.0
    hdr['LTM1_1'] = 1.0

    hdr['CTYPE2P'] = 'rawy'
    hdr['CRVAL2P'] = refrawy-0.5
    hdr['CRPIX2P'] = 0.5
    hdr['CDELT2P'] = 1.0

    hdr['WCSTY2P'] = 'PHYSICAL'
    hdr['LTV2'] = -refrawy+1.0
    hdr['LTM2_2'] = 1.0

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
