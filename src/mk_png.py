import argparse
import astropy.io.fits
import glob
import numpy as np
import os
import re
import sys

import HRCExp

def mk_png(indir, outdir):
    HRCExp.mkdir_p(outdir)

    ifiles = glob.glob(f'{indir}/hrc[is]-[0-9]_*.fits.gz')
    ifiles.sort()

    ofiles = [ f'{outdir}/'+re.search(r'([^/]+)\.fits.*$', f).groups()[0]+'.png' for f in ifiles]

    for i in range(len(ifiles)):
        ifile = ifiles[i]
        ofile = ofiles[i]

        sys.stderr.write(f'{ifile} -> {ofile}\n')
        HRCExp.fits2png_fitspng(ifile, ofile)

def main():
    parser = argparse.ArgumentParser(
        description='Create PNG images from HRC exposure maps.'
    )
    parser.add_argument('indir', help='Input directory.')
    parser.add_argument('outdir', help='Output directory.')
    args = parser.parse_args()
    mk_png(args.indir, args.outdir)

if __name__ == '__main__':
    main()
