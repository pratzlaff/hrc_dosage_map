import argparse
import astropy.io.fits
import glob
import numpy as np
import os
import re
import sys

import HRCDose

def mk_one_png(args):

    ifile, ofile = args.infile, args.outfile

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
        description='Create PNG image from HRC dosage map.'
    )
    parser.add_argument('infile')
    parser.add_argument('outfile')
    parser.add_argument('-n', '--noexec', action='store_true', help='Do not actually do anything.')
    parser.add_argument('--use', choices=('ds9', 'matplotlib', 'fitspng'), default='ds9')

    args = parser.parse_args()

    mk_one_png(args)

if __name__ == '__main__':
    main()
