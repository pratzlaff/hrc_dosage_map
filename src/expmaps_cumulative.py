import argparse
import astropy.io.fits
import glob
import numpy as np
import os
import re
import sys

import HRCExp

def expmaps_cumulative(indir, outdir):
    HRCExp.mkdir_p(outdir)

    y0, m0, y1, m1 = stop_start_months(indir)
    if y1==y0:
        nmonths = m1-m0+1
    else:
        nmonths = 13-m0+m1+ 12*(y1-y0-1)
    sys.stderr.write(f'Summing {nmonths} months, from {y0}-{m0:02} to {y1}-{m1:02}.\n')

    expmaps = HRCExp.mk_zero_expmaps()

    fmstats = { }
    fastats = { }

    year, month = y0, m0
    for j in range(nmonths):
        sys.stderr.write(f'{year}-{month:02d}\n')
        for det in expmaps:

            if det not in fmstats:
                fmstats[det] = []
                fastats[det] = []

            for i in range(len(expmaps[det])):

                # open stats files if this is the first time they're used
                if len(fmstats[det]) < i+1:
                    fmname = f'{outdir}/hrc{det}-{i}_stats_dff'
                    fmstats[det].append(open(fmname, 'w'))
                    faname = f'{outdir}/hrc{det}-{i}_stats_acc'
                    fastats[det].append(open(faname, 'w'))

                fname = f'{indir}/hrc{det}-{i}_{year}_{month:02}.fits.gz'

                if not os.path.isfile(fname):
                    sys.stderr.write(f'Could not open {fname}, continuing without.\n')
                    fmstats[det][i].write('\t'.join(f'{year}',f'{month}',*['NA']*8,'\n'))
                    fastats[det][i].write('\t'.join(f'{year}',f'{month}',*['NA']*8,'\n'))
                    continue

                with astropy.io.fits.open(fname) as hdul:
                    img = hdul[0].data
                    # if there were no observations during a month, will throw a
                    # ValuError when calling numpy.histogram with nbins=0
                    try:
                        s1, s2, s3 = sigma_values(img)
                    except:
                        fmstats[det][i].write('\t'.join([f'{year}',f'{month}',*['NA']*8,'\n']))
                        fastats[det][i].write('\t'.join([f'{year}',f'{month}',*['NA']*8,'\n']))
                        continue
                    out = calc_stats(img, det, i)
                    fmstats[det][i].write('\t'.join([
                        f'{year}',
                        f'{month}',
                        f'{out[0]:5.6f}',
                        f'{out[1]:5.6f}',
                        f'{out[2]:5.1f}',
                        f'({out[4]:.0f},{out[5]:.0f})',
                        f'{out[3]:5.1f}',
                        f'({out[6]:.0f},{out[7]:.0f})',
                        f'{s1:5.1f}',
                        f'{s2:5.1f}',
                        f'{s3:5.1f}',
                        '\n']))

                    expmaps[det][i] += img
                    out = calc_stats(expmaps[det][i], det, i)
                    s1, s2, s3 = sigma_values(expmaps[det][i])
                    fastats[det][i].write('\t'.join([
                        f'{year}',
                        f'{month}',
                        f'{out[0]:5.6f}',
                        f'{out[1]:5.6f}',
                        f'{out[2]:5.1f}',
                        f'({out[4]:.0f},{out[5]:.0f})',
                        f'{out[3]:5.1f}',
                        f'({out[6]:.0f},{out[7]:.0f})',
                        f'{s1:5.1f}',
                        f'{s2:5.1f}',
                        f'{s3:5.1f}',
                        '\n']))

        write_files(expmaps, y0, m0, year, month, outdir)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

def sigma_values(img):
    dmax = img.max()
    hcnt, bin_edges = np.histogram(img, bins=dmax, range=(0.5, dmax+0.5))
    hbin = 0.5*(bin_edges[1:] + bin_edges[:-1])
    vsum = hcnt.sum()
    
    if hbin.size > 0:
        v68 = int(0.68  * vsum)
        v95 = int(0.95  * vsum)
        v99 = int(0.997 * vsum)
        sigma1 = -999
        sigma2 = -999
        sigma3 = -999
        acc= 0
        for i in range(hbin.size):
            acc += hcnt[i]
            if acc > v68 and sigma1 < 0:
                sigma1 = hbin[i]
            elif acc > v95 and sigma2 < 0:
                sigma2 = hbin[i]
            elif acc > v99 and sigma3 < 0:
                sigma3 = hbin[i]
                break
    
        return sigma1, sigma2, sigma3
    else:
        return 0, 0, 0

def calc_stats(img, det, i):
    image = img.copy()
    #--- to avoid getting min value from the outside of the frame
    #--- edge of a CCD, set threshold
    image[image<0] = 0
    image[image>1e10] = 0
    mean = image.mean()
    dev = image.std()
    minx, miny = np.unravel_index(np.argmin(image), image.shape)
    maxx, maxy = np.unravel_index(np.argmax(image), image.shape)
    dmin = image[minx, miny]
    dmax = image[maxx, maxy]
    minx += HRCExp.subraw[det]['x'][0][i]
    maxx += HRCExp.subraw[det]['x'][0][i]
    miny += HRCExp.subraw[det]['y'][0][i]
    maxy += HRCExp.subraw[det]['y'][0][i]
    return mean,  dev,  dmin,  dmax , miny,  minx,  maxy,  maxx

def write_files(expmaps, y0, m0, y1, m1, outdir):
    for det in expmaps:
        for i in range(len(expmaps[det])):
            fname = f'{outdir}/hrc{det}-{i}_{y0}_{m0:02d}-{y1}_{m1:02d}.fits.gz'
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

def stop_start_months(indir):
    files = glob.glob(f'{indir}/hrci-0_*.fits.gz')
    files.sort()
    if not files:
        sys.stderr.write(f'no appropriate files found in {indir}\n')
        sys.exit(1)
    year0, month0 = re.search(r'(\d{4})_(\d{2})', files[0]).groups()[0:2]
    year1, month1 = re.search(r'(\d{4})_(\d{2})', files[-1]).groups()[0:2]
    return int(year0), int(month0), int(year1), int(month1)

def main():
    parser = argparse.ArgumentParser(
        description='Combine monthly exposure maps.'
    )
    parser.add_argument('indir', help='Input directory.')
    parser.add_argument('outdir', help='Output directory.')
    args = parser.parse_args()
    expmaps_cumulative(args.indir, args.outdir)

if __name__ == '__main__':
    main()
