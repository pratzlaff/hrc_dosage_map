#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       hrc_dose_get_data.py: obtain HRC Evt 1 data for a month and create              #
#                                cumulative data fits files in multiple image files     #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Mar 21, 2021                                                      #
#	VLK changed SQL user isobe to rpete (2021-nov-01)				#
#	VLK added -f flag to gzip (2021-nov-04)				#
#                                                                                       #
#########################################################################################

import astropy.io.fits
import numpy as np
import os
import re
import shutil
import sys
import tempfile

import HRCExp

# #
# #--- reading directory list
# #
# path = '/data/legs/rpete/flight/hrc_exposure_map/Scripts/house_keeping/dir_list'
# f    = open(path, 'r')
# data = [line.strip() for line in f.readlines()]
# f.close()

# for ent in data:
#     atemp = re.split(':', ent)
#     var  = atemp[1].strip()
#     line = atemp[0].strip()
#     exec("%s = %s" %(var, line))

#
#--- setting sections for subdividing image
#
RAWX0 = {
    'HRC-S' : [0 for i in range(10)],
    'HRC-I' : (   1,    1,     1,  5462,  5462,  5462, 10924, 10924, 10924),
}
RAWX1 = {
    'HRC-S' : [4095 for i in range(10)],
    'HRC-I' : (5461, 5461 , 5461, 10923, 10923, 10923, 16385, 16385, 16385),
}
RAWY0 = {
    'HRC-S' : (   1, 4916,  9832, 14748, 19664, 24580, 29496, 34412, 39328, 44244),
    'HRC-I' : (   1, 5462, 10924,     1,  5462, 10924,     1,  5562, 10942),
}
RAWY1 = {
    'HRC-S' : (4915, 9831, 14747, 19663, 24579, 29495, 34411, 39327, 44243, 49159),
    'HRC-I' : (5461,10923, 16385,  5461, 10923, 16385,  5461, 10923, 16385),
}


#---------------------------------------------------------------------------------------
#--- run_hrc_dose: run main hrc dose script by giving data extraction period    
#---------------------------------------------------------------------------------------

def run_hrc_dose(startYear, startMonth, stopYear, stopMonth):
    """
    run main hrc dose script by giving data extraction period
    input:  startYear   --- year of data collection start
            startMonth  --- month of data colleciton start
            stopYear    --- year of data collection stop
            stopMonth   --- month of data coloeciton stop
    output: <data_dir>/Month/Hrc<I/S>_<month>_<year>_<sec>.fits.gz        
            <data_dir>/Cumulative/Hrc<I/S>_08_1999_<month>_<year>_<sec>.fits.gz        
    """
    #
    #--- start extracting the data for the year/month period
    #
    for year in range(startYear, stopYear+1):

        #
        #---create a list of month appropriate for the year
        #
        month_list =  make_month_list(year, startYear, stopYear, startMonth, stopMonth)

        for month in month_list:

            #
            #--- extract the data for the month/year
            #
            hrc_dose_get_data(year, month)

#---------------------------------------------------------------------------------------
#-- hrc_dose_get_data: extract HRC evt1 data from a month and create cumulative data fits file
#---------------------------------------------------------------------------------------

def hrc_dose_get_data(year, month):
    """
    Extract HRC evt1 data from a month and create cumulative data fits file. 
    input:  year    --- year of data collection
            month   --- month of data colleciton
    output: <data_dir>/Month/Hrc<I/S>_<month>_<year>_<sec>.fits.gz        
            <data_dir>/Cumulative/Hrc<I/S>_08_1999_<month>_<year>_<sec>.fits.gz        
    """

    outfile_i = [f'HRCI_{month:02d}_{year}_{i}.fits' for i in range(9)]
    outfile_s = [f'HRCS_{month:02d}_{year}_{i}.fits' for i in range(10)]

    # HRC obsids within the specified year/month, and detector names
    obsids, insts = HRCExp.year_month_obsids(year, month)

    #
    #--- extract each evt1 file, extract the central part, and combine them into a one file
    #
    #---counters for how many observations are extracted for each detector
    #
    cnt = {
        'HRC-I' : [0 for i in range(9)],
        'HRC-S' : [0 for i in range(10)],
    }

    for i in range(obsids.size):
        obsid = obsids[i]
        detector = insts[i]
        archived=False
        try:
            fitsName = HRCExp.find_local_evt1(obsid)
        except:
            try:
                fitsName = HRCExp.retrieve_archived_evt1(obsid)
                archived=True
            except:
                raise Exception(f'could not file EVT1 file for obsid {obsid:05d}')

        sys.stderr.write("Processing: " + fitsName + ' : ' + detector+'\n')
        rawx, rawy = HRCExp.fits_read_raw(fitsName)

        if archived:
            os.unlink(fitsName)

        global RAWX0, RAWX1, RAWY0, RAWY1

        #
        #---- full image is divided into 10 sections
        #
        for i in range(0, 10):

            #
            #--- I has 9 sections, S has 10
            #
            if i>len(RAWX0[detector])-1:
                continue

            x0 = RAWX0[detector][i]
            x1 = RAWX1[detector][i]
            y0 = RAWY0[detector][i]
            y1 = RAWY1[detector][i]

            hist = HRCExp.raw_hist(rawx, rawy, x0, x1, y0, y1)

            with tempfile.TemporaryDirectory() as tmpdir:
                tmpfits = os.path.join(tmpdir, 'ztemp.fits')
                if hist.sum():
                    hdu = astropy.io.fits.PrimaryHDU(hist.astype(np.int32))
                    HRCExp.hdu_add_img_wcs(hdu, x0, y0)
                    hdul = astropy.io.fits.HDUList([hdu])
                    hdul.writeto(tmpfits, checksum=True, overwrite=True)
                    ichk = 1
                else:
                    sys.stderr.write(f'no counts: {fitsName}, [{x0}-{x1}, {y0}-{y1}]\n')
                    ichk = 0

                if (detector == 'HRC-S') and (ichk > 0):

                    #
                    #--- add ztemp.fits to fits, if there if no fits, mv ztemp.fits to fits
                    #
                    fits  = f'total_s{i}.fits'
                    if os.path.isfile(fits):
                        HRCExp.fits_img_add_inplace(tmpfits, fits)
                    else:
                        shutil.copyfile(tmpfits, fits)
                    cnt[detector][i] += 1

                elif (detector == 'HRC-I') and (ichk > 0):
                    fits  = f'total_i{i}.fits'
                    if os.path.isfile(fits):
                        HRCExp.fits_img_add_inplace(tmpfits, fits)
                    else:
                        shutil.copyfile(tmpfits, fits)
                    cnt[detector][i] += 1

    for i in range(0, 10):    
        if cnt['HRC-S'][i]:
            shutil.move(f'total_s{i}.fits', f'{HRCExp.data_s_dir}/Month/{outfile_s[i]}')
            os.system(f'gzip -f {HRCExp.data_s_dir}/Month/*.fits')
        createCumulative(year, month, 'HRC-S', HRCExp.data_s_dir, i)

    for i in range(0, 9):    
        if cnt['HRC-I'][i]:
            shutil.move(f'total_i{i}.fits', f'{HRCExp.data_i_dir}/Month/{outfile_i[i]}')
            os.system(f'gzip -f {HRCExp.data_i_dir}/Month/*.fits')
        createCumulative(year, month, 'HRC-I', HRCExp.data_i_dir, i)


#---------------------------------------------------------------------------------
#--- createCumulative: create cumulative hrc data                               --
#---------------------------------------------------------------------------------

def createCumulative(year, month, detector, arch_dir, i):
    """
    create cumulative hrc data for a given year and month
    input:  year        --- year
            month       --- month
            detector    --- detector: HRC_I/HRC_S
            arch_dir    --- the directory to save the data
            i           --- section of the image
    output: <data_dir>/Cumulative/Hrc<I/S>_08_1999_<month>_<year>_<sec>.fits.gz        
    """
#
#--- find the previous period
#
    pyear = year
    pmonth = month -1
    if pmonth < 1:
        pmonth = 12
        pyear -= 1

    if detector == 'HRC-I':
        inst = 'HRCI'
    else:
        inst = 'HRCS'
    #
    #--- set file names
    #
    dfile = f'{arch_dir}/Month/{inst}_{month:02d}_{year}_{i}.fits.gz'
    pfile = f'{arch_dir}/Cumulative/{inst}_08_1999_{pmonth:02d}_{pyear}_{i}.fits.gz'
    ofile = f'{arch_dir}/Cumulative/{inst}_08_1999_{month:02d}_{year}_{i}.fits.gz'

    #
    #--- if the monthly file exists, reduce the size of the file before combine it 
    #--- into a cumulative data
    #
    if os.path.isfile(dfile):
        if os.path.isfile(pfile):
            HRCExp.fits_img_add(dfile, pfile, ofile)
        else:
            shutil.copyfile(dfile, ofile)
    #
    #--- if the monthly file does not exist, copy the last month's cumulative data
    #
    else:
        shutil.copyfile(pfile, ofile)

#---------------------------------------------------------------------------------
#-- make_month_list: create an appropriate month list for a given conditions  ----
#---------------------------------------------------------------------------------

def make_month_list(year, startYear, stopYear, startMonth, stopMonth):
    """
    create an appropriate month list for a given conditions
    input: year, startYear, stopYear, startMonth, stopMonth
    """
    #
    #--- fill up the month list
    #
    month_list = []

    if startYear == stopYear:
        #
        #--- the period is in the same year
        #
        month_list = range(startMonth, stopMonth+1)
    else:
        #
        #--- if the period is over two or more years, we need to set three sets of month list
        #
        if year == startYear:
            month_list = range(startMonth, 13)
        elif year == stopYear:
            month_list = range(1,stopMonth+1)
        else:
            month_list = range(1,13)

    return month_list

if __name__ == '__main__':
    
    if len(sys.argv) > 4:
        start_year = int(float(sys.argv[1]))
        start_mon  = int(float(sys.argv[2]))
        stop_year  = int(float(sys.argv[3]))
        stop_mon   = int(float(sys.argv[4]))
        run_hrc_dose(start_year, start_mon, stop_year, stop_mon)

    elif len(sys.argv) > 2:
        year = int(float(sys.argv[1]))
        mon  = int(float(sys.argv[2]))
        hrc_dose_get_data(year, mon)
