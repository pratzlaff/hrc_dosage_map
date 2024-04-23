import argparse
import astropy.io.fits
import glob
import numpy as np
import os
import re
import sys

import HRCExp

def expmaps_cumulative(indir, outdir, check=False, det=None, subdet=None):
    if not check:
        HRCExp.mkdir_p(outdir)

    y0, m0, y1, m1 = stop_start_months(indir, det, subdet)
    if y1==y0:
        nmonths = m1-m0+1
    else:
        nmonths = 13-m0+m1+ 12*(y1-y0-1)
    sys.stderr.write(f'Summing {nmonths} months, from {y0}-{m0:02} to {y1}-{m1:02}.\n')

    expmaps = HRCExp.mk_zero_expmaps(det, subdet)

    year, month = y0, m0

    for j in range(nmonths):
        sys.stderr.write(f'{year}-{month:02d}\n')
        for det in expmaps:

            subdets = list(range(HRCExp.nsubdets(det)))
            if subdet is not None:
                subdets = [ subdet ]

            for i in subdets:
                fname = f'{indir}/hrc{det}{i}m_{year}-{month:02}.fits.gz'

                if not os.path.isfile(fname):
                    sys.stderr.write(f'Could not open {fname}, continuing without.\n')
                    continue

                if check:
                    continue

                with astropy.io.fits.open(fname) as hdul:
                    img = hdul[0].data
                    expmaps[det][i] += img

        if not check:
            write_files(expmaps, y0, m0, year, month, outdir)

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

def write_files(expmaps, y0, m0, y1, m1, outdir):
    for det in expmaps:
        for i in expmaps[det]:
            fname = f'{outdir}/hrc{det}{i}c_{y1}-{m1:02d}.fits.gz'
            rawx0 = HRCExp.subraw[det]['x'][0][i]
            rawy0 = HRCExp.subraw[det]['y'][0][i]
            expmap = expmaps[det][i]
            max = expmap.max()
            dtype = expmap.dtype
            if max <= np.iinfo(np.int8).max:
                dtype = np.int8
            elif max <= np.iinfo(np.int16).max:
                dtype = np.int16
            hdu = astropy.io.fits.PrimaryHDU(expmap.astype(dtype))
            HRCExp.hdu_add_img_wcs(hdu, rawx0, rawy0)
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
        description='Combine monthly exposure maps.'
    )
    parser.add_argument('-c', '--check', action='store_true', help='\
Check for the existence of any missing monthly exposure maps without \
doing anything else.')
    parser.add_argument('-d', '--det', choices=['i', 's'], help='\
Only calculate cumulative map for the given detector. Must be used \
in conjunction with -i.')
    parser.add_argument('-s', '--subdet', type=int, choices=range(10), help='\
Only calculate cumulative map for the given subdetector region. Must \
be used in conjunction with --det.')
    parser.add_argument('indir', help='Input directory.')
    parser.add_argument('outdir', help='Output directory.')
    args = parser.parse_args()
    expmaps_cumulative(args.indir, args.outdir, check=args.check, det=args.det, subdet=args.subdet)

if __name__ == '__main__':
    main()
