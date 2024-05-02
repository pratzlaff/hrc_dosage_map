#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       hrc_dose_create_image.py: convert hrc fits files to png image files                     #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                               #
#       last update: Mar 19, 2021                                                               #
#                                                                                               #
#################################################################################################

import fnmatch
import glob
import os
import re
import shutil
import string
import sys

import HRCExp

#
#--- this converts FITS files to image files
#
import mta_convert_fits_to_image as mtaimg


def fits2img(year, month, fdir, idir, wdir):
    """Converts all year/month FITS images in fdir to PNG in idir,
    then copying to wdir.
    """
    hname =  f'HRC*{month:02d}_{year}*.fits*'
    files = glob.glob(f'{fdir}/HRC*{month:02d}_{year}*.fits*')
    stem = [re.search(r'([^/]+)\.fits.*$', f).groups()[0] for f in files]
    for i in range(len(files)):
        oifile = f'{idir}/{stem[i]}.png'
        owfile = f'{wdir}/{stem[i]}.png'
        HRCExp.fits2png(files[i], oifile)
        shutil.copyfile(oifile, owfile)

def create_hrc_maps2(year, month):
    for inst in ('i', 's'):
        fdir = { 'i':HRCExp.data_i_dir, 's':HRCExp.data_s_dir }[inst]
        idir = { 'i':HRCExp.img_i_dir, 's':HRCExp.img_s_dir }[inst]
        wdir = { 'i':HRCExp.web_img_i_dir, 's':HRCExp.web_img_s_dir }[inst]
        for subd in 'Month', 'Cumulative':
            fits2img(year, month, f'{fdir}/{subd}/', f'{idir}/{subd}/', f'{wdir}/{subd}/')

#--------------------------------------------------------------------------------------------
#---  create_hrc_maps: create HRC image maps for given year and month                    ----
#--------------------------------------------------------------------------------------------

def create_hrc_maps(year, month, manual=0, chk=0):
    """
    create HRC image maps for given year and month 
    input:  year    --- year
            month   --- month
            manual  --- if > 0, ds9 is used to create images. 
            chk     --- if it is >0, 99.5% cut will be applied for the data in manual mode case
    output: <img_dir>/<Inst>/<Month>/Hrc<inst>_<month>_<year>.png
            <img_dir>/<Inst>/<Cumulative>/Hrc<inst>_08_1999_<month>_<year>.png
    """
#
#--- image for sections for full images
#
    for inst in ['Hrc_I', 'Hrc_S']:

        bdir = { 'Hrc_I':HRCExp.data_i_dir, 'Hrc_S':HRCExp.data_s_dir }[inst]
        idir = { 'Hrc_I':HRCExp.img_i_dir, 'Hrc_S':HRCExp.img_s_dir }[inst]
        idir2 = { 'Hrc_I':HRCExp.web_img_i_dir, 'Hrc_S':HRCExp.web_img_s_dir }[inst]
    
        mdir  = f'{bdir}/Month/'
        odir  = f'{idir}/Month/'
        odir2 = f'{idir2}Month/'
        if manual == 0:
            hrc_dose_conv_to_png(mdir, odir, year, month)
        else:
            hrc_dose_conv_to_png_manual(mdir, odir, odir2, year, month, chk=0)

        cdir  = f'{bdir}/Cumulative/'
        odir  = f'{idir}/Cumulative/'
        odir2 = f'{idir2}/Cumulative/'
        if manual == 0:
            hrc_dose_conv_to_png(cdir, odir, year, month)
        else:
            hrc_dose_conv_to_png_manual(cdir, odir, odir2,  year, month, chk=0)
    
    
#--------------------------------------------------------------------------------------------
#--- hrc_dose_conv_to_png: convet fits files into png images                              ---
#--------------------------------------------------------------------------------------------

def hrc_dose_conv_to_png(indir, outdir, year, month):
    """
    convet fits files into png images
    input:  indir   --- a directory where to find the data
            outdir  --- image output directory
            yeear   --- year
            month   --- month
    output: <img_dir>/<Inst>/<Month>/Hrc<inst>_<month>_<year>.png
            <img_dir>/<Inst>/<Month>/Hrc<inst>_08_1999_<month>_<year>.png
    """

    hname =  f'HRC*{month:02d}_{year}*.fits*'

    for ifile in os.listdir(indir):

        if fnmatch.fnmatch(ifile, hname):

            btemp   = re.split(r'\.fits', ifile)
            out     = btemp[0]
            outfile = outdir + out

            file_p  = f'{indir}/{ifile}'

            mtaimg.mta_convert_fits_to_image(file_p, outfile, 'linear', '125x125', 'sls', 'png')
            cmd = f'convert -trim {outfile}.png  ztemp.png'
            os.system(cmd)
            shutil.move('ztemp.png', f'{outfile}.png')
        else:
            pass

#--------------------------------------------------------------------------------------------
#--- hrc_dose_conv_to_png_manual: convet fits files into png images using ds9             ---
#--------------------------------------------------------------------------------------------

def hrc_dose_conv_to_png_manual(indir, outdir, outdir2, year, month, scale='sqrt', color='sls', chk=0):
    """
    convet fits files into png images using ds9. this must be used manually on screen
    input:  indir   --- a directory where to find the data
            outdir  --- image output directory
            outdir2 --- image output directory for html page
            yeear   --- year
            month   --- month
            sclae   --- scale, such sqrt, log, or linear
            color   --- color map name
            chk     --- if it is >0, 99.5% cut will be applied for the data
    output: <img_dir>/<Inst>/<Month>/Hrc<inst>_<month>_<year>.png
            <img_dir>/<Inst>/<Month>/Hrc<inst>_08_1999_<month>_<year>.png
    """
    hname =  f'HRC*{month:02d}_{year}*.fits*'

    for ifile in os.listdir(indir):

        if fnmatch.fnmatch(ifile, hname):

            btemp    = re.split(r'\.fits', ifile)
            out      = btemp[0]
            outfile  = f'{outdir}/{out}.png'
            outfile2  = f'{outdir2}/{out}.png'

            ifits   = f'{indir}/{ifile}'

            cmd = f'ds9 {ifits} -geometry 760x1024 -zoom to fit '
            if chk > 0:
                cmd += f'-scale mode 99.5  -scale {scale} -cmap {color}'
            else:
                cmd += f'-scale {scale}  -cmap {color}'

            cmd += ' -colorbar yes -colorbar vertical -colorbar numerics yes -colorbar space value '
            cmd += f' -colorbar fontsize 12  -saveimage png {outfile} -exit'

            os.system(cmd)
            shutil.copyfile(outfile, outfile2)
        else:
            pass

#--------------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv)  == 3:
        year  = int(float(sys.argv[1]))
        month = int(float(sys.argv[2]))
        create_hrc_maps(year, month)

    elif len(sys.argv) == 4:
        year   = int(float(sys.argv[1]))
        month  = int(float(sys.argv[2]))
        manual = int(float(sys.argv[3]))
        create_hrc_maps(year, month, manual)

    elif len(sys.argv) == 5:
        year   = int(float(sys.argv[1]))
        month  = int(float(sys.argv[2]))
        manual = int(float(sys.argv[3]))
        chk    = int(float(sys.argv[4]))
        create_hrc_maps(year, month, manual, chk)
    else:
        print("Usage: hrc_dose_create_image.py <year> <month> <manual:optional> <chk:optional>")


