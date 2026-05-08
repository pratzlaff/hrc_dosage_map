import argparse
import astropy.io.fits
import glob
import numpy as np
import os
import re
import sys

import HRCDose

def mk_png(indir, outdir, det, subdet, type, year, month, ds9, matplotlib, fitspng, clobber, noexec):
    HRCDose.mkdir_p(outdir)

    ifiles = glob.glob(f'{indir}/hrc{det}{subdet}{type}_{year}-{month}.fits.gz')
    ifiles.sort()

    ofiles = [ f'{outdir}/'+re.search(r'([^/]+)\.fits.*$', f).groups()[0]+'.png' for f in ifiles]

    for i in range(len(ifiles)):
        ifile = ifiles[i]
        ofile = ofiles[i]

        if os.path.isfile(ofile) and os.path.getmtime(ifile) < os.path.getmtime(ofile):
            if not clobber:
                sys.stderr.write(f'{ofile} exists and has mtime greater than {ifile}, skipping. Use --clobber to override\n')
                continue
        print(f'{ifile} -> {ofile}')

        det = re.search('hrc([is])[0-2][cm]', ofile).groups()[0]

        if (ds9):
            if noexec:
                sys.stderr.write("would run HRCDose.fits2png_ds9(ifile, ofile, det), but --noexec called\n")
            else:
                HRCDose.fits2png_ds9(ifile, ofile, det)
        if (matplotlib):
            if noexec:
                sys.stderr.write("would run HRCDose.fits2png_matplotlib(ifile, ofile), but --noexec called\n")
            else:
                HRCDose.fits2png_matplotlib(ifile, ofile)
        if (fitspng):
            if noexec:
                sys.stderr.write("would run HRCDose.fits2png_fitspng(ifile, ofile), but --noexec called\n")
            else:
                HRCDose.fits2png_fitspng(ifile, ofile)
        sys.stderr.flush()

def main():
    parser = argparse.ArgumentParser(
        description='Create PNG images from HRC dosage maps.'
    )
    parser.add_argument('indir', help='Input directory.')
    parser.add_argument('outdir', help='Output directory.')
    parser.add_argument('-d', '--det', default='[is]', help='Detector.')
    parser.add_argument('-s', '--subdet', default='[0-2]', help='Detector.')
    parser.add_argument('-t', '--type', default='[mc]', help='Detector.')
    parser.add_argument('-y', '--year', default='[0-9]'*4, help='Year.')
    parser.add_argument('-m', '--month', default='[0-9]'*2, help='Month.')
    parser.add_argument('-n', '--noexec', action='store_true', help='Do not actually do anything.')
    parser.add_argument('--ds9', action='store_true')
    parser.add_argument('--matplotlib', action='store_true')
    parser.add_argument('--fitspng', action='store_true')
    parser.add_argument('--clobber', action='store_true', help='Overwrite even if outfile already exists and has mtime later than infile.')

    args = parser.parse_args()
    mk_png(args.indir, args.outdir, args.det, args.subdet, args.type, args.year, args.month, args.ds9, args.matplotlib, args.fitspng, args.clobber, args.noexec)

if __name__ == '__main__':
    main()
