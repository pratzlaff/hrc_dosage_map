import argparse
import astropy.io.fits
import glob
import numpy as np
import os
import re
import sys

import HRCDose

def dosemap_year_month(fname):
    year, month = re.search(r'(\d{4})-(\d{2})', fname).groups()[0:2]
    return int(year), int(month)

def mk_stats(indir, outdir, det, subdet, cdir):
    HRCDose.mkdir_p(outdir)
    files = glob.glob(f'{indir}/hrc{det}{subdet}m_[0-9][0-9][0-9][0-9]-[0-9][0-9].fits.gz')
    files.sort()
    if not files:
        sys.stderr.write(f'no files found in {indir} for detector {det}:{subdet}\n')
        sys.exit(0)

    y0, m0 = dosemap_year_month(files[0])
    y1, m1 = dosemap_year_month(files[-1])

    if y1==y0:
        nmonths = m1-m0+1
    else:
        nmonths = 13-m0+m1+ 12*(y1-y0-1)

    if (nmonths != len(files)):
        sys.stderr.write(f'Expecting {nmonths} dosage files, only see {len(files)}.\n')
        sys.exit(1)

    fcfile = f'{outdir}/hrc{det}{subdet}c_stats'
    fmfile = f'{outdir}/hrc{det}{subdet}m_stats'
    nostats = [*['0']*3, '(1,1)', '0', '(1,1)', *['0']*3]

    dosemaps = HRCDose.mk_zero_dosemaps(det, subdet)

    # append mode
    if (os.path.isfile(fcfile) and os.path.isfile(fmfile)):
        if cdir is None:
            sys.stderr.write(f'Going into append mode, but --cdir unspecified.\n')
            sys.exit(1)
        cstats = HRCDose.read_stat_file(outdir, det, subdet, 'c')
        mstats = HRCDose.read_stat_file(outdir, det, subdet, 'm')

        # previous year and month
        py = cstats[0][-1]
        pm = cstats[1][-1]

        y0 = py
        m0 = pm+1
        if (m0 > 12):
            y0 += 1
            m0 = 1

        if y1==y0:
            nmonths = m1-m0+1
        else:
            nmonths = 13-m0+m1+ 12*(y1-y0-1)
        files=files[len(files)-nmonths:]

        if (py!=mstats[0][-1] or pm==mstats[0][-1]):
            sys.stderr.write(f'Pre-existing cumulative and monthly stats files are incompatible.\n')
            sys.exit(1)

        lcstats = [str(cstats[i][-1]) for i in range(len(cstats))]
        lcstats[0] = f'{y0}'
        lcstats[1] = f'{m0}'

        fm = open(fmfile, 'a')
        fc = open(fcfile, 'a')
        fname = f'{cdir}/hrc{det}{subdet}c_{py}-{pm:02}.fits.gz'
        dosemaps[det][subdet] += astropy.io.fits.open(fname)[0].data

    else:
        fm = open(fmfile, 'w')
        fc = open(fcfile, 'w')
        lcstats = ['1999', '8', *nostats]

    year, month = y0, m0
    for i in range(nmonths):
        sys.stderr.write(f'{files[i]}\n')
        year, month = dosemap_year_month(files[i])
        img = astropy.io.fits.open(files[i])[0].data
        # if there were no observations during a month, will throw a
        # ValuError when calling numpy.histogram with nbins=0
        try:
            s1, s2, s3 = sigma_values(img)
        except:
            fm.write('\t'.join([f'{year}',f'{month}',*nostats,'\n']))
            fc.write('\t'.join([*lcstats, '\n']))
            if month==12:
                lcstats[0] = f'{year+1}'
                lcstats[1] = '1'
            else:
                lcstats[1] = f'{month+1}'
            fm.flush()
            fc.flush()
            continue

        out = HRCDose.stats_img(img, det, subdet)

        fm.write('\t'.join([
            f'{year}',
            f'{month}',
            f'{out[0]:5.6f}',
            f'{out[1]:5.6f}',
            f'{out[2]:d}',
            f'({out[4]:.0f},{out[5]:.0f})',
            f'{out[3]:d}',
            f'({out[6]:.0f},{out[7]:.0f})',
            f'{s1:.0f}',
            f'{s2:.0f}',
            f'{s3:.0f}',
            '\n']))

        dosemaps[det][subdet] += img
        out = HRCDose.stats_img(dosemaps[det][subdet], det, subdet)
        s1, s2, s3 = sigma_values(dosemaps[det][subdet])
        lcstats = [
            f'{year}',
            f'{month}',
            f'{out[0]:5.6f}',
            f'{out[1]:5.6f}',
            f'{out[2]:d}',
            f'({out[4]:.0f},{out[5]:.0f})',
            f'{out[3]:d}',
            f'({out[6]:.0f},{out[7]:.0f})',
            f'{s1:.0f}',
            f'{s2:.0f}',
            f'{s3:.0f}',
        ]
        fc.write('\t'.join([*lcstats, '\n']))

        if month==12:
            lcstats[0] = f'{year+1}'
            lcstats[1] = '1'
        else:
            lcstats[1] = f'{month+1}'

        fm.flush()
        fc.flush()

def sigma_values(img):
    dmax = img.max()
    hcnt, bin_edges = np.histogram(img, bins=dmax, range=(0.5, dmax+0.5))
    hbin = 0.5*(bin_edges[1:] + bin_edges[:-1])
    vsum = hcnt.sum()
    
    if hbin.size > 0:
        v68 = int(0.68  * vsum)
        v95 = int(0.95  * vsum)
        v99 = int(0.997 * vsum)
        sigma1, sigma2, sigma3 = [0]*3
        acc= 0
        for i in range(hbin.size):
            acc += hcnt[i]
            if acc > v68 and sigma1 == 0:
                sigma1 = hbin[i]
            elif acc > v95 and sigma2 == 0:
                sigma2 = hbin[i]
            elif acc > v99 and sigma3 == 0:
                sigma3 = hbin[i]
                break
    
        return sigma1, sigma2, sigma3
    else:
        return 0, 0, 0

def main():
    parser = argparse.ArgumentParser(
        description='Combine monthly dosage maps.'
    )
    parser.add_argument('-c', '--cdir', help='Cumulative dosage map directory, required for append mode.')
    parser.add_argument('indir', help='Input directory.')
    parser.add_argument('outdir', help='Output directory.')
    parser.add_argument('det', choices=['i', 's'], help='Detector.')
    parser.add_argument('subdet', type=int, choices=list(range(10)), help='Subdetector.')
    
    args = parser.parse_args()
    mk_stats(args.indir, args.outdir,  args.det, args.subdet, args.cdir)

if __name__ == '__main__':
    main()
