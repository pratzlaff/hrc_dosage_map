import argparse
import astropy.io.fits
import glob
import numpy as np
import os
import re
import sys

import HRCDose

def mk_png(args):
    indir, outdir, subdet, type, year, month = (args.indir, args.outdir, args.subdet, args.type, args.year, args.month)
    HRCDose.mkdir_p(outdir)

    ifiles = glob.glob(f'{indir}/hrc{args.det}{subdet}{type}_{year}-{month}.fits.gz')
    ifiles.sort()

    ofiles = [ f'{outdir}/'+re.search(r'([^/]+)\.fits.*$', f).groups()[0]+'.png' for f in ifiles]

    for i in range(len(ifiles)):
        ifile = ifiles[i]
        ofile = ofiles[i]

        if os.path.isfile(ofile) and os.path.getmtime(ifile) < os.path.getmtime(ofile):
            if not args.clobber:
                continue
                sys.stderr.write(f'{ofile} exists and has mtime greater than {ifile}, skipping. Use --clobber to override\n')
                continue
        if args.filenames:
            print(f'{ifile} {ofile}')
            continue

        print(f'{ifile} ->  {ofile}')

        regex = 'hrc([is])[0-2][cm]'
        match = re.search(regex, ofile)
        if match := re.search(regex, ofile):
            det = match.groups()[0]
        else:
            raise ValueError(f'{ofile=} does not match {regex=}')

        pngargs = [ifile, ofile]

        if args.use == 'ds9':
            pngargs.append(det)

        use = { 'ds9':HRCDose.fits2png_ds9,
                'matplotlib':HRCDose.fits2png_matplotlib,
                'fitspng':HRCDose.fits2png_fitspng
               }

        usestr = { 'ds9':'HRCDose.fits2png_ds9',
                'matplotlib':'HRCDose.fits2png_matplotlib',
                'fitspng':'HRCDose.fits2png_fitspng'
               }

        if args.noexec:
                sys.stderr.write(f'would run {usestr[args.use]}({pngargs}), but --noexec called\n')
        else:
            use[args.use](*pngargs)

        sys.stderr.flush()

def main():
    parser = argparse.ArgumentParser(
        description='Create PNG images from HRC dosage maps.'
    )
    parser.add_argument('indir', help='Input directory.')
    parser.add_argument('outdir', help='Output directory.')
    parser.add_argument('--filenames', action='store_true', help='Only print input and output filenames.')
    parser.add_argument('-d', '--det', default='[is]', help='Detector.')
    parser.add_argument('-s', '--subdet', default='[0-2]', help='Detector.')
    parser.add_argument('-t', '--type', default='[mc]', help='Detector.')
    parser.add_argument('-y', '--year', default='[0-9]'*4, help='Year.')
    parser.add_argument('-m', '--month', default='[0-9]'*2, help='Month.')
    parser.add_argument('-n', '--noexec', action='store_true', help='Do not actually do anything.')
    parser.add_argument('--use', choices=('ds9', 'matplotlib', 'fitspng'), default='ds9')
    parser.add_argument('--clobber', action='store_true', help='Overwrite even if outfile already exists and has mtime later than infile.')

    args = parser.parse_args()

    mk_png(args)

if __name__ == '__main__':
    main()
