import argparse
import glob
import os
import numpy as np
import pprint
import re
import sys
import time

import HRCDose

chips = { 'i':['I'], 's':['S1', 'S2', 'S3'] }

def read_year_month(sfile):
    return np.loadtxt(sfile,
                      usecols=(0,1),
                      unpack=True,
                      dtype={'names':('year', 'month'),
                             'formats':('i2','i2')
                             }
                      )

def mk_html(sdir, pdir, tdir, outdir):

    HRCDose.mkdir_p(f'{outdir}/Sub_html')

    for det in HRCDose.subraw:
        for i in range(HRCDose.nsubdets(det)):
            create_html_page(sdir, det, i, tdir, outdir)

    create_main_html(sdir, tdir, outdir)

    year, month = read_year_month(f'{sdir}/hrci0m_stats')
    for i in range(year.size):
        create_img_html(pdir, tdir, outdir,
                        year=year[i], month=month[i],
                        next_month=(i<year.size-1)
                        )

def read_stat_file(sfile):
    names = ('year', 'month', 'mean', 'std',
             'min', 'minpos', 'max', 'maxpos',
             's1', 's2', 's3')
    formats = ('i2', 'i2', 'f4', 'f4',
               'i4', '<U14', 'i4', '<U14',
               'i2', 'i2', 'i2')
    return np.loadtxt(sfile, unpack=True, dtype={'names':names, 'formats':formats})

def create_html_page(sdir, det, i, tdir, outdir):
    global chips
    tdir = f'{tdir}/Templates'

    cdata = HRCDose.read_stat_file(sdir, det, i, 'c')
    mdata = HRCDose.read_stat_file(sdir, det, i, 'm')

    aline  = read_template(tdir, 'sub_top1')

    hname = { 'i':'HRC I', 's':'HRC S' }[det]
    inst = f'hrc{det}'

    aline += f'''<title>HRC-{chips[det][i]}: Historical Data</title>
</head>
<body style="color:white;background-color:black">
<div><a href="../hrc_dosage_map.html">Back to Top</a>
<h2 style="text-align:center">Data: HRC-{chips[det][i]}
'''

    links = []
    dets = HRCDose.dets()
    dets.sort()
    for d in dets:
        for subdet in range(HRCDose.nsubdets(d)):
            if (d != det or subdet != i):
                links.append(f'<a href="./hrc{d}{subdet}.html">{chips[d][subdet]}</a>')
    aline += '(' + ', '.join(links)+')'
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
        cmonth = HRCDose.change_month_format(months[j])
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

<div style="padding_top:10px; padding_bottom:10px;"><a href="../hrc_dosage_map.html">Back to Top</a>
'''

#
#--- add today's date as update date
#
    year, month, day = time.gmtime()[0:3]
    month = HRCDose.change_month_format(month)
    today = f'{month} {day}, {year}'

    aline += read_template(tdir, 'sub_footer').replace('#UPDATE#', today)

    outfile = f'{outdir}/Sub_html/{inst}{i}.html'
    with open(outfile, 'w') as fo:
        fo.write(aline)

#------------------------------------------------------------------------------------
#-- update_main_html: update the top html page                                     --
#------------------------------------------------------------------------------------

def create_main_html(sdir, tdir, outdir):
    tdir = f'{tdir}/Templates'
#
#--- display date
#
    year, month, day = time.gmtime()[0:3]
    month = HRCDose.change_month_format(month)
    today = f'{month} {day}, {year}'
#
#--- link date for the most recent plots
#
    lyear, lmon = find_last_entry_data(sdir)

    data  = read_template(tdir, 'main_page')
    data  = data.replace('#LATEST#', f'{lyear}-{lmon:02d}')
    data  = data.replace('#UPDATE#', today)

    ofile = f'{outdir}/hrc_dosage_map.html'
    with open(ofile, 'w') as fo:
        fo.write(data)

def find_last_entry_data(sdir):
    year, month = read_year_month(f'{sdir}/hrci0m_stats')
    return year[-1], month[-1]

def read_template(tdir, template):
    with open(f'{tdir}/{template}', 'r') as f:
        return f.read()

#------------------------------------------------------------------------------------
#-- create_img_html: create htmls to display dosage map                          --
#------------------------------------------------------------------------------------

def create_img_html(pdir, tdir, outdir, year=None, month=None, next_month=True):
    """
    create htmls to display dosage map.
    input:  year    --- year, if it is not given, the last month is used
            month   --- month, if it is not given, the last month is used
    output: <web_dir>/Image/HRC<inst>/Month/HRC<inst>_<mm>_<yyyy>_<sec>.html
            <web_dir>/Image/HRC<inst>/Cumulative/HRC<inst>_08_1999_<mm>_<yyyy>_<sec>.html
    """
    global chips
    tdir = f'{tdir}/Templates'
#
#--- find the current year/month
#
    cyear, cmonth = time.gmtime()[0:2]
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

    dets = HRCDose.dets()
    dets.sort()
    for inst in dets:
        cstop = HRCDose.nsubdets(inst)

        for sec in range(cstop):
#
#--- create image file link
#
            pnglink = f'../Image/hrc{inst}{sec}m_{ldate}.png'
#
#--- chip links
#
            links = []
            dets = HRCDose.dets()
            dets.sort()
            for d in dets:
                for subdet in range(HRCDose.nsubdets(d)):
                    if (d != inst or subdet != sec):
                        links.append(f'<a href="./hrc{d}{subdet}m_{ldate}.html">{chips[d][subdet]}</a>')
            seclink = ' '.join(links)+'<br />'
#
#--- time order link
#
            pfile = f'./hrc{inst}{sec}m_{pdate}.html'
            nfile = f'./hrc{inst}{sec}m_{ndate}.html'
            if year == 1999 and month == 8:
                tolink = f'<a href="{nfile}">Next Month</a><br />'
            elif not next_month:
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
            otemp = otemp.replace("#CHIP#",    chips[inst][sec])
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
    for inst in HRCDose.dets():
        nsec = HRCDose.nsubdets(inst)
        for sec in range(nsec):
#
#--- chip links
#
            links = []
            dets = HRCDose.dets()
            dets.sort()
            for d in dets:
                for subdet in range(HRCDose.nsubdets(d)):
                    if (d != inst or subdet != sec):
                        links.append(f'<a href="./hrc{d}{subdet}c_{ldate}.html">{chips[d][subdet]}</a>')
            seclink = ' '.join(links)+'<br />'
#
#--- time order links
#
            pfile = f'./hrc{inst}{sec}c_{pdate}.html'
            nfile = f'./hrc{inst}{sec}c_{ndate}.html'
            if year == 1999 and month == 8:
                tolink = f'<a href="{nfile}">Next Month</a><br />'
            elif not next_month:
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
            otemp = otemp.replace("#CHIP#",    chips[inst][sec])
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
        description='Create HTML pages from HRC dosage maps.'
    )
    parser.add_argument('--template_dir', default='./html', help='Directory containing HTML templates.')
    parser.add_argument('sdir', help='Stats directory.')
    parser.add_argument('pdir', help='PNG directory.')
    parser.add_argument('outdir', help='Output directory.')
    args = parser.parse_args()
    mk_html(args.sdir, args.pdir, args.template_dir, args.outdir)

if __name__ == '__main__':
    main()
