import argparse
import astropy.io.fits
import glob
import numpy as np
import os
import re
import sys

import HRCDose

def dosemaps_cumulative(indir, outdir, check=False, det=None, subdet=None, year=None, month=None):

    if not check:
        HRCDose.mkdir_p(outdir)

    dosemaps = HRCDose.mk_zero_dosemaps(det, subdet)

    if (year):
        y0 = y1 = year
        m0 = m1 = month
        pyear = year
        pmonth = month-1
        if pmonth<1:
            pyear -= 1
            pmonth = 12
        nmonths = 1

        for det in dosemaps:
            for subdet in dosemaps[det]:
                fname = f'{outdir}/hrc{det}{subdet}c_{pyear}-{pmonth:02}.fits.gz'
                dosemaps[det][subdet] += astropy.io.fits.open(fname)[0].data
    else:
        y0, m0, y1, m1 = stop_start_months(indir, det, subdet)
        if y1==y0:
            nmonths = m1-m0+1
        else:
            nmonths = 13-m0+m1+ 12*(y1-y0-1)
            sys.stderr.write(f'Summing {nmonths} months, from {y0}-{m0:02} to {y1}-{m1:02}.\n')

    year, month = y0, m0

    for j in range(nmonths):
        sys.stderr.write(f'{year}-{month:02d}\n')
        for det in dosemaps:
            for subdet in dosemaps[det]:
                print(det, subdet)
                fname = f'{indir}/hrc{det}{subdet}m_{year}-{month:02}.fits.gz'

                if not os.path.isfile(fname) and check:
                    sys.stderr.write(f'missing: {fname}\n')
                    continue

                with astropy.io.fits.open(fname) as hdul:
                    img = hdul[0].data
                    dosemaps[det][subdet] += img

        if not check:
            write_files(dosemaps, y0, m0, year, month, outdir)

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

def write_files(dosemaps, y0, m0, y1, m1, outdir):
    for det in dosemaps:
        for i in dosemaps[det]:
            fname = f'{outdir}/hrc{det}{i}c_{y1}-{m1:02d}.fits.gz'
            rawx0 = HRCDose.subraw[det]['x'][0][i]
            rawy0 = HRCDose.subraw[det]['y'][0][i]
            dosemap = dosemaps[det][i]
            max = dosemap.max()
            dtype = dosemap.dtype
            if max <= np.iinfo(np.int8).max:
                dtype = np.int8
            elif max <= np.iinfo(np.int16).max:
                dtype = np.int16
            hdu = astropy.io.fits.PrimaryHDU(dosemap.astype(dtype))
            HRCDose.hdu_add_img_wcs(hdu, rawx0, rawy0)
            hdul = astropy.io.fits.HDUList([hdu])
            hdul.writeto(fname, checksum=True, overwrite=True)

def stop_start_months(indir, det=None, subdet=None):
    if not det:
        det='i'
        subdet=0
    files = glob.glob(f'{indir}/hrc{det}{subdet}m_*.fits.gz')
    files.sort()
    if not files:
        sys.stderr.write(f'no appropriate files found in {indir}\n')
        sys.exit(1)
    year0, month0 = re.search(r'(\d{4})-(\d{2})', files[0]).groups()[0:2]
    year1, month1 = re.search(r'(\d{4})-(\d{2})', files[-1]).groups()[0:2]
    return int(year0), int(month0), int(year1), int(month1)

def main():
    parser = argparse.ArgumentParser(
        description='Combine monthly dosage maps.'
    )
    parser.add_argument('-c', '--check', action='store_true', help='\
Check for the existence of any missing monthly dosage maps without \
doing anything else.')
    parser.add_argument('-d', '--det', choices=['i', 's'], help='\
Only calculate cumulative map for the given detector. Must be used \
in conjunction with -i.')
    parser.add_argument('-s', '--subdet', type=int, choices=range(3), help='\
Only calculate cumulative map for the given subdetector region. Must \
be used in conjunction with --det.')
    parser.add_argument('-y', '--year', type=int, help='Process only the specified year and month.')
    parser.add_argument('-m', '--month', type=int, help='Process only the specified year and month.')
    parser.add_argument('indir', help='Input directory.')
    parser.add_argument('outdir', help='Output directory.')
    args = parser.parse_args()
    dosemaps_cumulative(args.indir,
                       args.outdir,
                       check=args.check,
                       det=args.det,
                       subdet=args.subdet,
                       year=args.year,
                       month=args.month)

if __name__ == '__main__':
    main()
