import argparse
import astropy.io.fits
import glob
import numpy as np
import os
import re
import sys

import HRCExp

def mk_png(indir, outdir, det, subdet, type, ds9, matplotlib, fitspng):
    HRCExp.mkdir_p(outdir)

    ifiles = glob.glob(f'{indir}/hrc{det}{subdet}{type}_[0-9][0-9][0-9][0-9]-[0-9][0-9].fits.gz')
    ifiles.sort()

    ofiles = [ f'{outdir}/'+re.search(r'([^/]+)\.fits.*$', f).groups()[0]+'.png' for f in ifiles]

    for i in range(len(ifiles)):
        ifile = ifiles[i]
        ofile = ofiles[i]

        det = re.search('hrc([is])[0-2][cm]', ofile).groups()[0]

        sys.stderr.write(f'{ifile} -> {ofile}\n')
        if (ds9):
            HRCExp.fits2png_ds9(ifile, ofile, det)
        if (matplotlib):
            HRCExp.fits2png_matplotlib(ifile, ofile)
        if (fitspng):
            HRCExp.fits2png_fitspng(ifile, ofile)

def main():
    parser = argparse.ArgumentParser(
        description='Create PNG images from HRC exposure maps.'
    )
    parser.add_argument('indir', help='Input directory.')
    parser.add_argument('outdir', help='Output directory.')
    parser.add_argument('-d', '--det', default='[is]', help='Detector.')
    parser.add_argument('-s', '--subdet', default='[0-2]', help='Detector.')
    parser.add_argument('-t', '--type', default='[mc]', help='Detector.')
    parser.add_argument('--ds9', action='store_true')
    parser.add_argument('--matplotlib', action='store_true')
    parser.add_argument('--fitspng', action='store_true')

    args = parser.parse_args()
    mk_png(args.indir, args.outdir, args.det, args.subdet, args.type, args.ds9, args.matplotlib, args.fitspng)

if __name__ == '__main__':
    main()
