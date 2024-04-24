import argparse
import glob
import os
import numpy as np
import pprint
import re
import sys
import time

import HRCExp

    # hrc_dose_html_updates.hrc_dose_make_data_html()
    # hrc_dose_html_updates.update_main_html()
    # hrc_dose_html_updates.create_img_html()

def mk_html(sdir, pdir, tdir, outdir):

    HRCExp.mkdir_p(f'{outdir}/Sub_html')

    for det in HRCExp.subraw:
        nsub = len(HRCExp.subraw[det]['x'][0])
        for i in range(nsub):
            create_html_page(sdir, det, i, tdir, outdir)
    update_main_html(sdir, tdir, outdir)

    year, month = np.loadtxt(f'{sdir}/hrci0m_stats', usecols=(0,1), unpack=True,
                             dtype={'names':('year', 'month'), 'formats':('i2','i2')})
    for i in range(year.size):
        create_img_html(pdir, tdir, outdir, year=year[i], month=month[i])

def read_stat_file(sfile):
    names = ('year', 'month', 'mean', 'std',
             'min', 'minpos', 'max', 'maxpos',
             's1', 's2', 's3')
    formats = ('i2', 'i2', 'f4', 'f4',
               'i4', '<U14', 'i4', '<U14',
               'i2', 'i2', 'i2')

    return np.loadtxt(sfile, unpack=True, dtype={'names':names, 'formats':formats})

def create_html_page(sdir, det, i, tdir, outdir):
    tdir = f'{tdir}/Templates'

    cdata = HRCExp.read_stat_file(sdir, det, i, 'c')
    mdata = HRCExp.read_stat_file(sdir, det, i, 'm')

    nsub = HRCExp.nsubdets(det)
    aline  = read_template(tdir, 'sub_top1')

    hname = { 'i':'HRC I', 's':'HRC S' }[det]
    inst = f'hrc{det}'

    aline += f'''<title>{hname} Section: {i} History Data</title>
</head>
<body style="color:white;background-color:black">
<div><a href="../hrc_exposure_map.html">Back to Top</a>
<h2 style="text-align:center">Data: {hname} Section: {i}
'''

    if nsub > 1:
        if i == 0:
            aline += f' (<a href="./{inst}{i+1}.html">Next</a>)'
        elif i == nsub-1:
            aline += f' (<a href="./{inst}{i-1}.html">Prev</a>)'
        else:
            aline += f' (<a href="./{inst}{i-1}.html">Prev</a> : <a href="./{inst}{i+1}.html">Next</a>)'

    aline += '''</h2>
<div style='padding-bottom:30px'>
<table border=1>
'''
    aline += read_template(tdir, 'sub_col_header')
#
#--- open the data to indivisual lists
#
    years,months,mean_acc,std_acc,min_acc,min_apos, \
        max_acc,max_apos,asig1, asig2, asig3 = cdata
    mean_dff ,std_dff, min_dff, min_dpos,max_dff,max_dpos,\
        dsig1, dsig2, dsig3 = mdata[2:]

    dlen = len(years)
    for j in range(dlen):

        month = months[j]
        year = years[j]

#--- converting digit to letters, i.e. 1 to Jan
#
        cmonth = HRCExp.change_month_format(months[j])
#
#--- monthly HRC dose data
#
        aline += f'<tr><td>{year}</td><td>{month}</td>'

        aline += f'\
<td>{mean_dff[j]:4.4f}</td>\
<td>{std_dff[j]:4.4f}</td>\
<td>{max_dff[j]}</td>\
<td>{max_dpos[j]}</td>\
<td>{dsig1[j]}</td>\
<td>{dsig2[j]}</td>\
<td>{dsig3[j]}</td>\n'

        aline += f'<td><a href="./{inst}{i}m_{year}-{month:02d}.html">map</a></td>\n'

#
#---- cumulative HRC dose data
#
        aline += f'\
<td>{mean_acc[j]:4.4f}</td>\
<td>{std_acc[j]:4.4f}</td>\
<td>{max_acc[j]}</td>\
<td>{max_apos[j]}</td>\
<td>{asig1[j]}</td>\
<td>{asig2[j]}</td>\
<td>{asig3[j]}</td>\n'
  
        aline += f'<td><a href="./{inst}{i}c_{year}-{month:02d}.html">map</a></td></tr>\n'

#
#--- put header every new year so that we can read data easier
#
        if not months[j]%12 and j != (dlen-1):
           aline += read_template(tdir, 'sub_col_header')

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

    aline += read_template(tdir, 'sub_footer').replace('#UPDATE#', today)

    outfile = f'{outdir}/Sub_html/{inst}{i}.html'
    with open(outfile, 'w') as fo:
        fo.write(aline)

#------------------------------------------------------------------------------------
#-- update_main_html: update the top html page                                     --
#------------------------------------------------------------------------------------

def update_main_html(sdir, tdir, outdir):
    """
    update the top html page --- changes are just updated date
    input:  none, but read from <house_keeping>/exp_template
    output: <web_dir>/exposure.html
    """
    tdir = f'{tdir}/Templates'
#
#--- display date
#
    year, month, day = time.gmtime()[0:3]
    month = HRCExp.change_month_format(month)
    today = f'{month} {day}, {year}'
#
#--- link date for the most recent plots
#
    [lyear, lmon] = find_last_entry_data(sdir)

    line = f'{lyear}-{lmon:02d}'

    data  = read_template(tdir, 'main_page')
    data  = data.replace('#LATEST#', line)
    data  = data.replace('#UPDATE#', today)

    ofile = f'{outdir}/hrc_exposure_map.html'
    with open(ofile, 'w') as fo:
        fo.write(data)

def find_last_entry_data(sdir):
    year, month = np.loadtxt(f'{sdir}/hrci0m_stats', usecols=(0,1), unpack=True,
                             dtype={'names':('year', 'month'), 'formats':('i2','i2')})
    return year[-1], month[-1]

def read_template(tdir, template):
    with open(f'{tdir}/{template}', 'r') as f:
        return f.read()

#------------------------------------------------------------------------------------
#-- create_img_html: create htmls to display exposure map                          --
#------------------------------------------------------------------------------------

def create_img_html(pdir, tdir, outdir, year=None, month=None):
    """
    create htmls to display exposure map.
    input:  year    --- year, if it is not given, the last month is used
            month   --- month, if it is not given, the last month is used
    output: <web_dir>/Image/HRC<inst>/Month/HRC<inst>_<mm>_<yyyy>_<sec>.html
            <web_dir>/Image/HRC<inst>/Cumulative/HRC<inst>_08_1999_<mm>_<yyyy>_<sec>.html
    """
    tdir = f'{tdir}/Templates'
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
    ldate  = f'{year}-{month:02d}'
    pdate  = f'{pyear}-{pmonth:02d}'
    ndate  = f'{nyear}-{nmonth:02d}'

    monthly = read_template(tdir, 'mon_img_page')
    for inst in HRCExp.dets():
        cstop = HRCExp.nsubdets(inst)

        for sec in range(cstop):
#
#--- create image file link
#
            pnglink = f'../Image/hrc{inst}{sec}m_{ldate}.png'
#
#--- create link paths
#
            pfile = f'./hrc{inst}{sec}m_{pdate}.html'
            nfile = f'./hrc{inst}{sec}m_{ndate}.html'
            psfile = f'./hrc{inst}{sec-1}m_{ldate}.html'
            nsfile = f'./hrc{inst}{sec+1}m_{ldate}.html'
#
#--- section link
#
            seclink = ''
            if cstop>1:
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
            sublink = f'./hrc{inst}{sec}.html'
#
#--- cumulative link
#
            cumlink = f'<a href="./hrc{inst}{sec}c_{ldate}.html">Cumulative Plot</a>'
#
#--- replace texts in the template
#
            otemp = monthly
            otemp = otemp.replace("#YEAR#",    f'{year}')
            otemp = otemp.replace("#MONTH#",   f'{month:02d}')
            otemp = otemp.replace("#INST#",    inst.upper())
            otemp = otemp.replace("#SEC#",     f'{sec}')
            otemp = otemp.replace("#PNGLINK#", pnglink)
            otemp = otemp.replace("#LATEST#",  ldate)
            otemp = otemp.replace("#CUMLINK#", cumlink)
            otemp = otemp.replace("#SECLINK#", seclink)
            otemp = otemp.replace("#TOLINK#",  tolink)
            otemp = otemp.replace("#SUBLINK#", sublink)
#
#--- set output fine name
#
            ofile = f'{outdir}/Sub_html/hrc{inst}{sec}m_{ldate}.html'
            with open(ofile, 'w') as fo:
                fo.write(otemp)
#
#--- cumulative page
#
    cumulative  = read_template(tdir, 'cum_img_page')
    for inst in HRCExp.dets():
        nsec = HRCExp.nsubdets(inst)
        for sec in range(nsec):
#
#--- create link paths
#
            pfile = f'./hrc{inst}{sec}c_{pdate}.html'
            nfile = f'./hrc{inst}{sec}c_{ndate}.html'
            psfile = f'./hrc{inst}{sec-1}c_{ldate}.html'
            nsfile = f'./hrc{inst}{sec+1}c_{ldate}.html'
#
#--- section link
#
            seclink = ''
            if nsec>1:
                if sec == 0:
                    seclink = f'<a href="{nsfile}">Next Section</a><br />'
                elif sec == cstop-1:
                    seclink = f'<a href="{psfile}">Prev Section</a><br />'
                else:
                    seclink = f'<a href="{psfile}">Prev Section</a>  <a href="{nsfile}">Next Section</a><br />'
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
            sublink = f'./hrc{inst}{sec}.html'
#
#--- month link
#
            monlink = f'<a href="./hrc{inst}{sec}m_{ldate}.html">'
            monlink = monlink + 'Month Plot</a>' 
#
#--- replace texts in the template
#
            pnglink = f'../Image/hrc{inst}{sec}c_{ldate}.png'

            otemp = cumulative
            otemp = otemp.replace("#YEAR#",    f'{year}')
            otemp = otemp.replace("#MONTH#",   f'{month:02d}')
            otemp = otemp.replace("#INST#",    inst.upper())
            otemp = otemp.replace("#SEC#",     f'{sec}')
            otemp = otemp.replace("#PNGLINK#", pnglink)
            otemp = otemp.replace("#MONLINK#", monlink)
            otemp = otemp.replace("#SECLINK#", seclink)
            otemp = otemp.replace("#TOLINK#",  tolink)
            otemp = otemp.replace("#SUBLINK#", sublink)
#
#--- set output fine name
#
            ofile = f'{outdir}/Sub_html/hrc{inst}{sec}c_{ldate}.html'
            with open(ofile, 'w') as fo:
                fo.write(otemp)

def main():
    parser = argparse.ArgumentParser(
        description='Create HTML pages from HRC exposure maps.'
    )
    parser.add_argument('--template_dir', default='./html', help='Directory containing HTML templates.')
    parser.add_argument('sdir', help='Stats directory.')
    parser.add_argument('pdir', help='PNG directory.')
    parser.add_argument('outdir', help='Output directory.')
    args = parser.parse_args()
    mk_html(args.sdir, args.pdir, args.template_dir, args.outdir)

if __name__ == '__main__':
    main()
