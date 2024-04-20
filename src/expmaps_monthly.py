import argparse
import astropy.io.fits
import numpy as np
import os
import sys

import HRCExp

def expmaps_monthly(year, month, outdir):
    HRCExp.mkdir_p(outdir)

    expmaps = HRCExp.mk_zero_expmaps()

    # HRC obsids within the specified year/month, and detector names
    obsids, insts = HRCExp.year_month_obsids(year, month)

    for i in range(obsids.size):
        obsid = obsids[i]
        det = { 'HRC-I':'i', 'HRC-S':'s' }[insts[i]]

        archived=False
        try:
            evt1 = HRCExp.find_local_evt1(obsid)
        except:
            try:
                evt1 = HRCExp.retrieve_archived_evt1(obsid)
                archived=True
            except:
                sys.stderr.write(f'could not retrieve EVT1 file for obsid {obsid:05d}\n')
                continue

        sys.stderr.write(f'Processing: {evt1} : {det}\n')
        rawx, rawy = HRCExp.fits_read_raw(evt1)
        if archived:
            os.unlink(fitsName)

        nsub = len(expmaps[det])
        for i in range(nsub):
            x0 = HRCExp.subraw[det]['x'][0][i]
            x1 = HRCExp.subraw[det]['x'][1][i]
            y0 = HRCExp.subraw[det]['y'][0][i]
            y1 = HRCExp.subraw[det]['y'][1][i]
            expmaps[det][i] += HRCExp.raw_hist(rawx, rawy, x0, x1, y0, y1)

    write_files(expmaps, year, month, outdir)

def write_files(expmaps, year, month, outdir):
    for det in expmaps:
        for i in range(len(expmaps[det])):
            fname = f'{outdir}/hrc{det}-{i}_{year}_{month:02d}.fits.gz'
            x0 = HRCExp.subraw[det]['x'][0][i]
            y0 = HRCExp.subraw[det]['y'][0][i]
            expmap = expmaps[det][i]
            max = expmap.max()
            dtype = expmap.dtype
            #if max <= np.iinfo(np.int8).max:
                #dtype = np.int8
            if max <= np.iinfo(np.int16).max:
                dtype = np.int16
            hdu = astropy.io.fits.PrimaryHDU(expmap.astype(dtype))
            HRCExp.hdu_add_img_wcs(hdu, x0, y0)
            hdul = astropy.io.fits.HDUList([hdu])
            hdul.writeto(fname, checksum=True, overwrite=True)

def main():
    parser = argparse.ArgumentParser(
        description='Create tar file containing evt1 files for a given year/month.',
    )
    parser.add_argument('-o' , '--outdir', default='./foo', help='Output directory.')
    parser.add_argument('year', type=int)
    parser.add_argument('month', type=int)
    args = parser.parse_args()
    expmaps_monthly(args.year, args.month, args.outdir)

if __name__ == '__main__':
    main()
