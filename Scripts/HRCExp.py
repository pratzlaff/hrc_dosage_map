import astropy.io.fits
import glob
import numpy as np
import os
import re
import shutil
import subprocess

#
#--- reading directory list
#
path = '/data/legs/rpete/flight/hrc_exposure_map/Scripts/house_keeping/dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

def fits2png(infile, outfile):
    subprocess.run(['fitspng', '-l', '0,1', '-o', outfile, infile])

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
        #--- to avoid getting min value from the outside of the frame
        #--- edge of a CCD, set threshold
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

def change_month_format(month):
    """
    cnvert month format between digit and three letter month
    input:  month   --- either digit month or letter month
    oupupt: either digit month or letter month
    """
    m_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',\
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#
#--- check whether the input is digit
#
    try:
        var = int(float(month))
        if (var < 1) or (var > 12):
            return 'NA'
        else:
            return m_list[var-1]
#
#--- if not, return month #
#
    except:
        mon = 'NA'
        var = month.lower()
        for k in range(0, 12):
            if var == m_list[k].lower():
                return k+1

        return mon

def read_ocat():
    ocat='/data/legs/rpete/flight/hrc_exposure_map/Scripts/house_keeping/sot_ocat.out'
    mdict = {
        'Jan':1,
        'Feb':2,
        'Mar':3,
        'Apr':4,
        'May':5,
        'Jun':6,
        'Jul':7,
        'Aug':8,
        'Sep':9,
        'Oct':10,
        'Nov':11,
        'Dec':12,
    }

    obsids = []
    years = []
    months = []
    inst = []

    with open(ocat) as f:
        for line in f:
            cols = [s.strip() for s in line.split('^')]
            if cols[13] != 'NULL':
                m = re.search(r'(\w+)\s+\d+\s+(\d+)', cols[13])
                if m:
                    obsids.append(int(cols[1]))
                    inst.append(cols[12])
                    months.append(int(mdict[m.groups()[0]]))
                    years.append(int(m.groups()[1]))
    return np.array(obsids), np.array(years), np.array(months), np.array(inst)

def year_month_obsids(year, month):
    obsids, years, months, insts = read_ocat()
    mask = (years==year) & (months==month) & ((insts=='HRC-I')|(insts=='HRC-S'))
    return obsids[mask], insts[mask]

def retrieve_archived_evt1(obsid):
    input = f'''
operation=retrieve
dataset=flight
obsid={obsid:05d}
detector=hrc
filetype=evt1
level=1
go
'''
    p = subprocess.Popen(
        ['/proj/axaf/simul/bin/arc5gl', '-stdin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    output = p.communicate(input=input.encode())[0].decode()
    try:
        return re.search('hrcf.*_evt1.fits.gz', output).group()
    except:
        raise Exception(f'no archived EVT1 file found for obsid {obsid:05d}')

def send_email(address, message):
    p = subprocess.Popen(
        ['mailx', '-sSubject: HRC Exposure Map Processed', address],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    output = p.communicate(input=message.encode())[0].decode()

def find_local_evt1(obsid):
    files = glob.glob(f'/data/hrc/[is]/{obsid:05d}/secondary/hrcf{obsid:05d}_*evt1.fits*')
    if files:
        return files[0]
    else:
        raise Exception(f'no local evt1 file found for obsid {obsid:05d}')
