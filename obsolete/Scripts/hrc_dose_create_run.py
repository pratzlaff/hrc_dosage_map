#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       hrc_dose_create_run.py: a master scripts to run HRC scripts                             #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                               #
#       last update: Sep 27, 2021                                                               #
#       VLK 2021-nov-4: changed admin from swolk to vkashyap                                    #
#                                                                                               #
#################################################################################################

import os
import re
import string
import sys
import time

import hrc_dose_get_data            #--- extract data
import hrc_dose_create_image        #--- create png files
import hrc_dose_stat_data           #--- compute statistics
import hrc_dose_html_updates        #--- update html pages
import hrc_dose_plot_exposure_stat  #--- create stat plot

import HRCExp

admin = 'pratzlaff@cfa.harvard.edu'

#--------------------------------------------------------------------------------------------
#-- hrc_dose_create_run: a master scripts to run HRC scripts                               --
#--------------------------------------------------------------------------------------------

def hrc_dose_create_run(year='', month=''):
    """
    a master scripts to run HRC scripts
    input:  year --- year
            month   --- month
            if they are not given, the script will use the previous month's year/month
    output: HRC data in <data_dir> and png image files in <img_dir>
    """
#
#-- find today's date
#
    if year == '':
        year, month, mday = time.gmtime()[0:3]
    else:
        year  = int(year)
        month = int(month)
        mday  = 30
#
#--- if it is the first 10 days of the month, update for the previous month
#
    if mday >1 and mday < 10:
        month -= 1
        if month < 1:
            month = 12
            year -= 1
#
#--- run scripts
#

#     t0 = time.time()
#     hrc_dose_get_data.hrc_dose_get_data(year, month)
#     t1 = time.time()
#     sys.stderr.write(f'hrc_dose_get_data(): {t1-t0:.1f} seconds\n')

# #   hrc_dose_create_image.hrc_dose_create_image(year, month)

#     t0 = time.time()
#     #hrc_dose_create_image.create_hrc_maps(year, month)
#     hrc_dose_create_image.create_hrc_maps2(year, month)
#     sys.stderr.write(f'create_hrc_maps(): {time.time()-t0:.1f} seconds\n')

    t0 = time.time()
    hrc_dose_stat_data.hrc_dose_extract_stat_data_month(year, month)
    sys.stderr.write(f'hrc_dose_extract_stat_data_month(): {time.time()-t0:.1f} seconds\n')

    t0 = time.time()
    hrc_dose_plot_exposure_stat.hrc_dose_plot_exposure_stat(HRCExp.plt_dir)
    sys.stderr.write(f'hrc_dose_plot_exposure_stat(): {time.time()-t0:.1f} seconds\n')

    hrc_dose_html_updates.hrc_dose_make_data_html()
    hrc_dose_html_updates.update_main_html()
    hrc_dose_html_updates.create_img_html()
#
#--- update the date links of the image html page of the one month before the current ones
#
    lyear   = year
    lmonth  = month -1
    if lmonth < 1:
        lmonth = 12
        lyear -= 1
    hrc_dose_html_updates.create_img_html(lyear, lmonth)

#
#--- send email to admin
#
    text = f'''\
HRC Exposure maps for {year}/{month} were processed.
You still need to run:
/data/legs/rpete/flight/hrc_exposure_map/Scripts/hrc_dose_create_image.py {year} {month+1}
'''
    global admin
    HRCExp.send_email(admin, text)

#--------------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv)  == 3:
        year  = int(float(sys.argv[1]))
        month = int(float(sys.argv[2]))
    else:
        year  = ''
        month = ''

    hrc_dose_create_run(year, month)
