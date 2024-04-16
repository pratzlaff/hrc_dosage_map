#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#   hrc_dose_html_updates.py:   create  html data pages for a report                    #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Mar 19, 2021                                                       #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import time

import HRCExp

web_address= 'https://hea-www.harvard.edu/~rpete/HRC_Exposure/'
web_address = 'https://cxc.cfa.harvard.edu/contrib/cxchrc/HRC_Exposure/'
web_address= 'file:///data/wdocs/rpete/HRC_Exposure/'

#------------------------------------------------------------------------------------------------
#--- hrc_dose_plot_exposure_stat: read hrc database, and plot history of exposure             ---
#------------------------------------------------------------------------------------------------

def hrc_dose_make_data_html():
    """
    read hrc database, and create html page: 
    input:  indir   --- data directory
            output  --- output
    output: <web_dir>/Sub_html/<inst>_<sec>.html; a table of stat results
    """
    for hrc in ('hrci', 'hrcs'):
#
#--- hrc i has 9 sections and hrc s has 10 sections
#
        cstop = { 'hrci':9, 'hrcs':10 }[hrc]
        indir = { 'hrci':HRCExp.stat_i_dir, 'hrcs':HRCExp.stat_s_dir }[hrc]

        for sec in range(cstop):
            hrc_sec = f'{hrc}_{sec}'
#
#--- a trend data file contains following columns:
#---    year,month,mean_acc,std_acc,min_acc,min_apos, 
#---    max_acc,max_apos,asig1, asig2, asig3, mean_dff,std_dff,
#---    min_dff, min_dpos,max_dff,max_dpos, dsig1, dsig2, dsig3
#
            data = read_stat_data(indir, hrc_sec)
#
#--- create a HTML page to display histrical data
#
            create_html_page(data, hrc, sec, cstop)

#--------------------------------------------------------------------------------
#--  create_html_page: create HTML page to display HRC historical data       ----
#--------------------------------------------------------------------------------

def create_html_page(data, hrc, sec, ctop):
    """
    create HTML page to display HRC historical data.
    input:  data --- a list of lists of data:
                date,year,month,mean_acc,std_acc,min_acc,min_apos, 
                max_acc,max_apos,asig1, asig2, asig3, mean_dff,std_dff,
                min_dff, min_dpos,max_dff,max_dpos, dsig1, dsig2, dsig3
            hrc --- hrci or hrcs
            sec --- section
            ctop    --- max number of section
    output: <web_dir>/Sub_html/<inst>_<sec>.html
    """
#
#--- start composing HTML page
#
    aline  = read_template('sub_top1')

    hname = { 'hrci':'HRC I', 'hrcs':'HRC S' }[hrc]
    wname = { 'hrci':'HRCI', 'hrcs':'HRCS' }[hrc]
    inst = { 'hrci':'i', 'hrcs':'s' }[hrc]

    aline += f'''<title>{hname} Section: {sec} History Data</title>
</head>
<body style="color:white;background-color:black">
<div><a href="../hrc_exposure_map.html">Back to Top</a>
<h2 style="text-align:center">Data: {hname} Section: {sec}
'''

    if sec == 0:
        aline += f' (<a href="./hrc{inst}_{sec+1}.html">Next</a>)'
    elif sec == ctop-1:
        aline += f' (<a href="./hrc{inst}_{sec-1}.html">Prev</a>)'
    else:
        aline += f' (<a href="./hrc{inst}_{sec-1}.html">Prev</a> : <a href="./hrc{inst}_{sec+1}.html">Next</a>)'

    aline += '''</h2>
<div style='padding-bottom:30px'>
<table border=1>
'''
    aline += read_template('sub_col_header')
#
#--- open the data to indivisual lists
#
    [years,months,mean_acc,std_acc,min_acc,min_apos, \
     max_acc,max_apos,asig1, asig2, asig3, mean_dff,std_dff,\
     min_dff, min_dpos,max_dff,max_dpos,dsig1, dsig2, dsig3] = data

    dlen = len(years)
    for i in range(dlen):

        month = int(months[i])
        year = int(years[i])

#--- converting digit to letters, i.e. 1 to Jan
#
        cmonth = HRCExp.change_month_format(months[i])
#
#--- monthly HRC dose data
#
        if mean_dff[i] == 0 and std_dff[i] == 0:
            aline += f'<tr><td>{year}</td><td>{month:02d}</td>' + read_template('sub_nodata')
        else:
            aline += f'<tr><td>{year}</td><td>{month}</td>'
            try:
                aline += f'\
<td>{mean_dff[i]:4.4f}</td>\
<td>{std_dff[i]:4.4f}</td>\
<td>{max_dff[i]:4.1f}</td>\
<td>{max_dpos[i]}</td>\
<td>{dsig1[i]:4.1f}</td>\
<td>{dsig2[i]}</td>\
<td>{dsig3[i]:4.1f}</td>\n'

#               if hrc == 'hrci':
#                   aline = aline + '<td><a href="' + HRCExp.data_i_dir + '/Month/'
#               else:
#                   aline = aline + '<td><a href="' + HRCExp.data_s_dir + '/Month/'
#               aline = aline +  wname + '_' + smonth + '_' + str(syear) + '.fits.gz">fits</a></td>\n'


                aline += f'<td><a href="{web_address}Image/{wname}/Month/{wname}_{month:02d}_{year}_{sec}.html">map</a></td>\n'
            except:
#
#--- for the case there is no data, print 'na'
#
                aline += '<td>na</td>'*7 + '\n<td>na</td>\n'

#
#---- cumulative HRC dose data
#
        aline += f'\
<td>{mean_acc[i]:4.4f}</td>\
<td>{std_acc[i]:4.4f}</td>\
<td>{max_acc[i]:4.1f}</td>\
<td>{max_apos[i]}</td>\
<td>{asig1[i]:4.1f}</td>\
<td>{asig2[i]}</td>\
<td>{asig3[i]:4.1f}</td>\n'
  
#        if hrc == 'hrci':
#            aline = aline + '<td><a href="' + HRCExp.data_i_dir + '/Cumulative/'
#        else:
#            aline = aline + '<td><a href="' + HRCExp.data_s_dir + '/Cumulative/'
#        aline = aline +  wname + '_' + smonth + '_' + str(syear) + '.fits.gz">fits</a></td>\n'

        aline += f'<td><a href="{web_address}Image/{wname}/Cumulative/{wname}_08_1999_{month:02d}_{year}_{sec}.html">map</a></td>\n'

#
#--- put header every new year so that we can read data easier
#
        if months[i] % 12 == 0 and i != (dlen-1):
            aline += read_template('sub_col_header')

    aline += '''\
</table>

<div style="padding_top:10px; padding_bottom:10px;"><a href="../hrc_exposure_map.html">Back to Top</a>
'''

#
#--- add today's date as update date
#
    year, month, day = time.gmtime()[0:3]
    month = HRCExp.change_month_format(month)
    today = f'{month} {day}, {year}'

    aline += read_template('sub_footer').replace('#UPDATE#', today)

    outdir = f'{HRCExp.web_dir}/Sub_html/{hrc}_{sec}.html'
    with open(outdir, 'w') as fo:
        fo.write(aline)

#------------------------------------------------------------------------------------
#-- update_main_html: update the top html page                                     --
#------------------------------------------------------------------------------------

def update_main_html():
    """
    update the top html page --- changes are just updated date
    input:  none, but read from <house_keeping>/exp_template
    output: <web_dir>/exposure.html
    """
#
#--- display date
#
    year, month, day = time.gmtime()[0:3]
    month = HRCExp.change_month_format(month)
    today = f'{month} {day}, {year}'
#
#--- link date for the most recent plots
#
    [lyear, lmon] = find_last_entry_data()

    line = f'{int(lmon):02d}_{lyear}'

    data  = read_template('main_page')
    data  = data.replace('#LATEST#', line)
    data  = data.replace('#UPDATE#', today)

    ofile = f'{HRCExp.web_dir}hrc_exposure_map.html'
    with open(ofile, 'w') as fo:
        fo.write(data)

#------------------------------------------------------------------------------------
#-- create_img_html: create htmls to display exposure map                          --
#------------------------------------------------------------------------------------

def create_img_html(year=None, month=None):
    """
    create htmls to display exposure map.
    input:  year    --- year, if it is not given, the last month is used
            month   --- month, if it is not given, the last month is used
    output: <web_dir>/Image/HRC<inst>/Month/HRC<inst>_<mm>_<yyyy>_<sec>.html
            <web_dir>/Image/HRC<inst>/Cumulative/HRC<inst>_08_1999_<mm>_<yyyy>_<sec>.html
    """
#
#--- find the current year/month
#
    cyear, cmonth = time.gmtime()[0:2]
    chk = 0
#
#--- if the year and month were not passed, set them to those of the last month
#
    if not year:
        year = cyear
        month = cmonth-1
        if month < 1:
            year -= 1
            month = 12
    else:
        year = int(year)
        month = int(month)
        if year < cyear:
            chk = 1
#
#--- set one month before and one month after
#
    pyear  = year
    pmonth = month - 1
    if pmonth < 1:
        pmonth =12 
        pyear -= 1

    nyear  = year
    nmonth = month + 1
    if nmonth > 12:
        nmonth = 1
        nyear += 1
#
#--- set link dates
#
    ldate  = f'{month:02d}_{year}'
    pdate  = f'{pmonth:02d}_{pyear}'
    ndate  = f'{nmonth:02d}_{nyear}'

    monthly = read_template('mon_img_page')
    for  inst in ('S', 'I'):

        cstop = { 'I':9,
                  'S':10
                 }[inst]

        odir = { 'I':HRCExp.web_img_i_dir,
                 'S':HRCExp.web_img_s_dir
                }[inst] + '/Month/'

        for sec in range(cstop):
#
#--- create image file link
#
            png = f'HRC{inst}_{ldate}_{sec}.png'
            cpath = f'{HRCExp.web_dir}Image/HRC{inst}/Month/{png}'
            if os.path.isfile(cpath):
                pnglink = './' + png
            else:
                pnglink = './no_data.png'
#
#--- create link paths
#
            pfile = f'./HRC{inst}_{pdate}_{sec}.html'
            nfile = f'./HRC{inst}_{ndate}_{sec}.html'
            psfile = f'./HRC{inst}_{ldate}_{sec-1}.html'
            nsfile = f'./HRC{inst}_{ldate}_{sec+1}.html'
#
#--- section link
#
            if sec == 0:
                seclink = f'<a href="{nsfile}">Next Section</a><br />'
            elif sec == cstop-1:
                seclink = f'<a href="{psfile}">Prev Section</a><br />'
            else:
                seclink = f'<a href="{psfile}">Prev Section</a>  <a href="{nsfile}">next Section</a><br />'
#
#--- time order link
#
            if year == 1999 and month == 8:
                tolink = f'<a href="{nfile}">Next Month</a><br />'
            elif chk == 0:
                tolink = f'<a href="{pfile}">Prev Month</a><br /> '
            else:
                tolink = f'<a href="{pfile}">Prev Month</a>  <a href="{nfile}">Next Month</a><br />'
#
#--- section main link
#
            sublink = f'../../../Sub_html/hrc{inst.lower()}_{sec}.html'
#
#--- cumulative link
#
            cumlink = f'<a href="../Cumulative/HRC{inst}_08_1999_{ldate}_{sec}.html">Cumulative Plot</a>'
#
#--- replace texts in the template
#
            otemp = monthly
            otemp = otemp.replace("#YEAR#",    f'{year}')
            otemp = otemp.replace("#MONTH#",   f'{month:02d}')
            otemp = otemp.replace("#INST#",    inst)
            otemp = otemp.replace("#SEC#",     str(sec))
            otemp = otemp.replace("#PNGLINK#", pnglink)
            otemp = otemp.replace("#LATEST#",  ldate)
            otemp = otemp.replace("#CUMLINK#", cumlink)
            otemp = otemp.replace("#SECLINK#", seclink)
            otemp = otemp.replace("#TOLINK#",  tolink)
            otemp = otemp.replace("#SUBLINK#", sublink)
#
#--- set output fine name
#
            ofile = f'{odir}/HRC{inst}_{ldate}_{sec}.html'
            with open(ofile, 'w') as fo:
                fo.write(otemp)
#
#--- cumulatvie page
#
    cumulative  = read_template('cum_img_page')
    for  inst in ('S', 'I'):
        cstop = { 'I':9,
                  'S':10
                 }[inst]

        odir = { 'I':HRCExp.web_img_i_dir,
                 'S':HRCExp.web_img_s_dir
                }[inst] + '/Cumulative/'

        for sec in range(cstop):
#
#--- create link paths
#
            pfile = f'./HRC{inst}_08_1999_{pdate}_{sec}.html'
            nfile = f'./HRC{inst}_08_1999_{ndate}_{sec}.html'
            psfile = f'./HRC{inst}_08_1999_{ldate}_{sec-1}.html'
            nsfile = f'./HRC{inst}_08_1999_{ldate}_{sec+1}.html'
#
#--- section link
#
            if sec == 0:
                seclink = f'<a href="{nsfile}">next Section</a><br />'
            elif sec == cstop-1:
                seclink = f'<a href="{psfile}">Prev Section</a><br />'
            else:
                seclink = f'<a href="{psfile}">Prev Section</a>  <a href="{nsfile}">next Section</a><br />'
#
#--- time order link
#
            if year == 1999 and month == 8:
                tolink = f'<a href="{nfile}">Next Month</a><br />'
            elif chk == 0:
                tolink = f'<a href="{pfile}">Prev Month</a><br /> '
            else:
                tolink = f'<a href="{pfile}">Prev Month</a>  <a href="{nfile}">Next Month</a><br />'
#
#--- section main link
#
            sublink = f'../../../Sub_html/hrc{inst.lower()}_{sec}.html'
#
#--- month link
#
            monlink = f'<a href="../Month/HRC{inst}_{ldate}_{sec}.html">'
            monlink = monlink + 'Month Plot</a>' 
#
#--- replace texts in the template
#
            otemp = cumulative
            otemp = otemp.replace("#YEAR#",    f'{year}')
            otemp = otemp.replace("#MONTH#",   f'{month:02d}')
            otemp = otemp.replace("#INST#",    inst)
            otemp = otemp.replace("#SEC#",     f'{sec}')
            otemp = otemp.replace("#LATEST#",  ldate)
            otemp = otemp.replace("#MONLINK#", monlink)
            otemp = otemp.replace("#SECLINK#", seclink)
            otemp = otemp.replace("#TOLINK#",  tolink)
            otemp = otemp.replace("#SUBLINK#", sublink)
#
#--- set output fine name
#
            ofile = f'{odir}/HRC{inst}_08_1999_{ldate}_{sec}.html'
            print(ofile)
            with open(ofile, 'w') as fo:
                fo.write(otemp)

#------------------------------------------------------------------------------------
#-- read_stat_data: read data from acis/hrc history data files                    ---
#------------------------------------------------------------------------------------

def read_stat_data(indir, inst):
    """
    read data from acis/hrc history data files
    input:  indir--- directory where the data locate
            inst --- instruments hrci_<section>, hrcs_<section>
    output: a list of lists
            [year,month,mean_acc,std_acc,min_acc,min_apos, max_acc,\
            max_apos,asig1, asig2, asig3, mean_dff,std_dff,min_dff, \
            min_dpos,max_dff,max_dpos,dsig1, dsig2, dsig3]
    """
    ifile = f'{indir}{inst}_acc_out'
    data  = HRCExp.read_data_file(ifile)
    save  = convert_to_columndata(data)

    ifile = f'{indir}{inst}_dff_out'
    data  = HRCExp.read_data_file(ifile)
    save2 = convert_to_columndata(data)
# 
#--- odata contains:
#---  [year,month,mean_acc,std_acc,min_acc,min_apos, max_acc,\
#---   max_apos,asig1, asig2, asig3, mean_dff,std_dff,min_dff, \
#---   min_dpos,max_dff,max_dpos,dsig1, dsig2, dsig3]
#
    odata = save + save2[2:]   #--- skipping date part from the second list
    return odata

#------------------------------------------------------------------------------------
#-- convert_to_columndata: convert a list of data into a list of lists            ---
#------------------------------------------------------------------------------------

def convert_to_columndata(data):
    """
    convert a list of data into a list of lists
    input:  data    --- a list of data
    output: save    --- a list of lists of data
    """

    slen = len(re.split(r'\s+', data[0]))
    save = []
    for k in range(0, slen):
        save.append([])

    for ent in data:
        out = re.split(r'\s+', ent)
        for k in range(0, slen):
            try:
                save[k].append(float(out[k]))
            except:
                save[k].append(out[k])

    return save

#------------------------------------------------------------------------------------
#-- read_template: read a template                                                 --
#------------------------------------------------------------------------------------

def read_template(part):
    """
    read a template
    input:  part    --- a file name which contain the template
    output: out     --- a text
    """
    ifile = HRCExp.house_keeping + 'Templates/' + part
    with open(ifile, 'r') as f:
        out = f.read()

    return out

#------------------------------------------------------------------------------------
#-- find_last_entry_data: find the last entry date from a data file                --
#------------------------------------------------------------------------------------

def find_last_entry_data():
    """
    find the last entry date from a data file
    input: none, but read from <stat_i_dir>/hrci_4_acc_out
    output: [<year>, <month>]
    """
    ifile = f'{HRCExp.stat_i_dir}/hrci_4_acc_out'
    data  = HRCExp.read_data_file(ifile)

    atemp = re.split(r'\s+', data[-1])

    return [atemp[0], atemp[1]]


#------------------------------------------------------------------------------------

if __name__ == '__main__':

    update_main_html()

    if len(sys.argv) > 2:
        year = int(float(sys.argv[1]))
        mon  = int(float(sys.argv[2]))
        create_img_html(year, mon)
    else:
        hrc_dose_make_data_html()
        update_main_html()
        create_img_html()

#    for year in range(1999, 2020):
#        for mon in range(1, 13):
#            if year == 1999 and mon < 8:
#                continue
#            print("TIME: " + str(year) + ' : ' + str(mon))
#            create_img_html(year, mon)



