import argparse
import astropy.io.fits
import numpy as np
import os
import sys

import HRCDose

def dosemaps_monthly(args):
    year = args.year
    month = args.month
    outdir = args.outdir

    HRCDose.mkdir_p(outdir)

    dosemaps = HRCDose.mk_zero_dosemaps()

    try:
        obsids = HRCDose.year_month_obsids_archive(year, month)
    except:
        obsids = HRCDose.year_month_obsids_ocat(year, month)
    print(obsids)

    for i in range(obsids.size):
        obsid = obsids[i]

        archived=False
        try:
            evt1 = HRCDose.find_local_evt1(obsid)
        except:
            try:
                evt1 = HRCDose.retrieve_archived_evt1(obsid)
                archived=True
            except:
                sys.stderr.write(f'could not retrieve EVT1 file for obsid {obsid:05d}\n')
                continue

        det = { 'HRC-I':'i', 'HRC-S':'s' }[HRCDose.detnam(evt1)]
        sys.stderr.write(f'Processing: {evt1} : {det}\n')
        rawx, rawy = HRCDose.fits_read_raw(evt1)
        if archived:
            os.unlink(evt1)

        nsub = len(dosemaps[det])
        for i in range(nsub):
            x0 = HRCDose.subraw[det]['x'][0][i]
            x1 = HRCDose.subraw[det]['x'][1][i]
            y0 = HRCDose.subraw[det]['y'][0][i]
            y1 = HRCDose.subraw[det]['y'][1][i]
            dosemaps[det][i] += HRCDose.raw_hist(rawx, rawy, x0, x1, y0, y1)

    write_files(dosemaps, year, month, outdir)

def write_files(dosemaps, year, month, outdir):
    for det in dosemaps:
        for i in dosemaps[det]:
            fname = f'{outdir}/hrc{det}{i}m_{year}-{month:02d}.fits.gz'
            x0 = HRCDose.subraw[det]['x'][0][i]
            y0 = HRCDose.subraw[det]['y'][0][i]
            dosemap = dosemaps[det][i]
            max = dosemap.max()
            dtype = dosemap.dtype
            if max <= np.iinfo(np.int8).max:
                dtype = np.int8
            elif max <= np.iinfo(np.int16).max:
                dtype = np.int16
            hdu = astropy.io.fits.PrimaryHDU(dosemap.astype(dtype))
            HRCDose.hdu_add_img_wcs(hdu, x0, y0)
            hdul = astropy.io.fits.HDUList([hdu])
            hdul.writeto(fname, checksum=True, overwrite=True)

def main():
    parser = argparse.ArgumentParser(
        description='Create dosage maps for a given year/month.'
    )
    parser.add_argument('year', type=int)
    parser.add_argument('month', type=int)
    parser.add_argument('outdir', help='Output directory.')
    args = parser.parse_args()

    dosemaps_monthly(args)

if __name__ == '__main__':
    main()
