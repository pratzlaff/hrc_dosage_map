import argparse
import astropy.io.fits
import glob
import numpy as np
import os
import re
import sys

import HRCExp

def mk_png(indir, outdir, det, subdet, type):
    HRCExp.mkdir_p(outdir)

    ifiles = glob.glob(f'{indir}/hrc{det}{subdet}{type}_[0-9][0-9][0-9][0-9]-[0-9][0-9].fits.gz')
    ifiles.sort()

    ofiles = [ f'{outdir}/'+re.search(r'([^/]+)\.fits.*$', f).groups()[0]+'.png' for f in ifiles]

    for i in range(len(ifiles)):
        ifile = ifiles[i]
        ofile = ofiles[i]

        sys.stderr.write(f'{ifile} -> {ofile}\n')
        HRCExp.fits2png_matplotlib(ifile, ofile)

def main():
    parser = argparse.ArgumentParser(
        description='Create PNG images from HRC exposure maps.'
    )
    parser.add_argument('indir', help='Input directory.')
    parser.add_argument('outdir', help='Output directory.')
    parser.add_argument('-d', '--det', default='[is]', help='Detector.')
    parser.add_argument('-s', '--subdet', default='[0-2]', help='Detector.')
    parser.add_argument('-t', '--type', default='[mc]', help='Detector.')
    args = parser.parse_args()
    mk_png(args.indir, args.outdir, args.det, args.subdet, args.type)

if __name__ == '__main__':
    main()
