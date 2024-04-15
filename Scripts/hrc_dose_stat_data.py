#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       hrc_dose_stat_data.py: extract statistics from HRC S and I files                        #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                               #
#       last update: Mar 19, 2021                                                               #
#                                                                                               #
#################################################################################################

import astropy.io.fits
import numpy as np
import os
import random
import re
import string
import sys
import time

import HRCExp

#------------------------------------------------------------------------------------------
#--- comp_stat: compute statistics for the hrc image and print out the result            --
#------------------------------------------------------------------------------------------

def comp_stat(ifile, year, month, ofile):
    """
    compute statistics for the hrc image and print out the result 
    input: ifile    --- hrc image file 
            year    --- year 
            month   --- month, 
            ofile   --- output file name.
    output: ofile   --- a file with stat results updated
    """
    if os.path.isfile(ifile):
        out = HRCExp.stats(ifile)
        if out[3]>0:
            (sig1, sig2, sig3) = find_sigma_values(ifile)

        else:
            out = ('NA','NA','NA','NA','NA','NA','NA','NA')
            (sig1, sig2, sig3) = ('NA', 'NA', 'NA')

    else:
        out = ('NA','NA','NA','NA','NA','NA','NA','NA')
        (sig1, sig2, sig3) = ('NA', 'NA', 'NA')
#
#--- print out the results
#
    if out[0] == 'NA':
        line = '%d\t%d\t' % (year, month)
        line =  line + 'NA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\n'
    else:
        line = '%d\t%d\t' % (year, month)
        line = line +  '%5.6f\t'   % float(out[0])
        line = line +  '%5.6f\t'   % float(out[1])
        line = line +  '%5.1f\t'   % float(out[2])
        line = line +  '(%d,%d)\t' % (float(out[4]), float(out[5]))
        line = line +  '%5.1f\t'   % float(out[3])
        line = line +  '(%d,%d)\t' % (float(out[6]), float(out[7]))
        line = line +  '%5.1f\t'   % float(sig1)
        line = line +  '%5.1f\t'   % float(sig2)
        line = line +  '%5.1f\n'   % float(sig3)

    if os.path.isfile(ofile):
        with open(ofile, 'a') as fo:
            fo.write(line)
    else:
        with open(ofile, 'w') as fo:
            fo.write(line)


#------------------------------------------------------------------------------------------
#-- find_sigma_values: find 2 sigma, 3sigma, and 4 sigma values of the given data        --
#------------------------------------------------------------------------------------------
        
def find_sigma_values(fits):
    """
    find 2 sigma, 3sigma, and 4 sigma values of the given data
    input:  fits    --- image fits file name
    output: (sigma1, sigma2, sigma3)
    """
    #
    #-- make histgram
    #-- checking one sigma and two sigma counts
    #
    hcnt, bin_edges = HRCExp.fits_img_hist(fits)
    hbin = 0.5*(bin_edges[1:] + bin_edges[:-1])
    vsum = hcnt.sum()

    # if len(hbin) > 0:
    if hbin.size > 0:
        v68 = int(0.68  * vsum)
        v95 = int(0.95  * vsum)
        v99 = int(0.997 * vsum)
        sigma1 = -999
        sigma2 = -999
        sigma3 = -999
        acc= 0
        # for i in range(0, len(hbin)):
        for i in range(0, hbin.size):
            acc += hcnt[i]
            if acc > v68 and sigma1 < 0:
                sigma1 = hbin[i]

            elif acc > v95 and sigma2 < 0:
                sigma2 = hbin[i]

            elif acc > v99 and sigma3 < 0:
                sigma3 = hbin[i]
                break
    
        return (sigma1, sigma2, sigma3)
    
    else:
        return(0, 0, 0)

#------------------------------------------------------------------------------------------
#--- hrc_dose_extract_stat_data_month: compute HRC statistics                           ---
#------------------------------------------------------------------------------------------

def hrc_dose_extract_stat_data_month(year='NA', month='NA'):
    """
    compute HRC statistics
    input   year    --- year
            month   --- month
    output: <stat_dir>/<inst>_<sec>_acc_out
            <stat_dir>/<inst>_<sec>_dff_out
    """
    if year == 'NA' or month == 'NA':
        year  = raw_input('Year: ')
        month = raw_input('Month: ')
    
    year  = int(year)
    month = int(month)

    syear  = str(year)
    smonth = str(month)
    if month < 10:
        smonth = '0' + smonth

    for i in range(0,10):
        ifile = f'{HRCExp.data_s_dir}/Cumulative/HRCS_08_1999_{month:02d}_{year}_{i}.fits.gz'
        out   = f'{HRCExp.stat_s_dir}/hrcs_{i}_acc_out'
        comp_stat(ifile, year, month, out)

        ifile = f'{HRCExp.data_s_dir}/Month/HRCS_{month:02d}_{year}_{i}.fits.gz' 
        out   = f'{HRCExp.stat_s_dir}/hrcs_{i}_dff_out'
        comp_stat(ifile, year, month, out)

    for i in range(0,9):
        ifile = f'{HRCExp.data_i_dir}/Cumulative/HRCI_08_1999_{month:02d}_{year}_{i}.fits.gz'
        out   = f'{HRCExp.stat_i_dir}/hrci_{i}_acc_out'
        comp_stat(ifile, year, month, out)

        ifile = f'{HRCExp.data_i_dir}/Month/HRCI_{month:02d}_{year}_{i}.fits.gz' 
        out   = f'{HRCExp.stat_i_dir}/hrci_{i}_dff_out'
        comp_stat(ifile, year, month, out)

#--------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    year  = int(sys.argv[1])
    month = int(sys.argv[2])

    hrc_dose_extract_stat_data_month(year, month)
