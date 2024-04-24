import argparse
import astropy.io.fits
import glob
import numpy as np
import re
import sys

import HRCExp

def mk_stats(indir, outdir, det, subdet):
    HRCExp.mkdir_p(outdir)
    files = glob.glob(f'{indir}/hrc{det}{subdet}m_[0-9][0-9][0-9][0-9]-[0-9][0-9].fits.gz')
    files.sort()
    if not files:
        sys.stderr.write(f'no files found in {indir} for detector {det}:{subdet}\n')
        sys.exit(0)

    expmaps = HRCExp.mk_zero_expmaps(det, subdet)

    fa = open(f'{outdir}/hrc{det}{subdet}c_stats', 'w')
    fm = open(f'{outdir}/hrc{det}{subdet}m_stats', 'w')
    nostats = [*['0']*3, '(1,1)', '0', '(1,1)', *['0']*3]
    lastats = ['1999', '8', *nostats]

    for fname in files:
        sys.stderr.write(f'{fname}\n')
        year, month = re.search(r'(\d{4})-(\d{2})', fname).groups()[0:2]
        year = int(year)
        month = int(month)
        with astropy.io.fits.open(fname) as hdul:
            img = hdul[0].data
            # if there were no observations during a month, will throw a
            # ValuError when calling numpy.histogram with nbins=0
            try:
                s1, s2, s3 = sigma_values(img)
            except:
                fm.write('\t'.join([f'{year}',f'{month}',*nostats,'\n']))
                fa.write('\t'.join([*lastats, '\n']))
                if month==12:
                    lastats[0] = f'{year+1}'
                    lastats[1] = '1'
                else:
                    lastats[1] = f'{month+1}'
                fm.flush()
                fa.flush()
                continue
            out = HRCExp.stats_img(img, det, subdet)

            fm.write('\t'.join([
                f'{year}',
                f'{month}',
                f'{out[0]:5.6f}',
                f'{out[1]:5.6f}',
                f'{out[2]:d}',
                f'({out[4]:.0f},{out[5]:.0f})',
                f'{out[3]:d}',
                f'({out[6]:.0f},{out[7]:.0f})',
                f'{s1:5.1f}',
                f'{s2:5.1f}',
                f'{s3:5.1f}',
                '\n']))

            expmaps[det][subdet] += img
            out = HRCExp.stats_img(expmaps[det][subdet], det, subdet)
            s1, s2, s3 = sigma_values(expmaps[det][subdet])
            lastats = [
                f'{year}',
                f'{month}',
                f'{out[0]:5.6f}',
                f'{out[1]:5.6f}',
                f'{out[2]:d}',
                f'({out[4]:.0f},{out[5]:.0f})',
                f'{out[3]:d}',
                f'({out[6]:.0f},{out[7]:.0f})',
                f'{s1:5.1f}',
                f'{s2:5.1f}',
                f'{s3:5.1f}',
            ]
            fa.write('\t'.join([*lastats, '\n']))
            
            if month==12:
                lastats[0] = f'{year+1}'
                lastats[1] = '1'
            else:
                lastats[1] = f'{month+1}'

            fm.flush()
            fa.flush()

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

def main():
    parser = argparse.ArgumentParser(
        description='Combine monthly exposure maps.'
    )
    parser.add_argument('indir', help='Input directory.')
    parser.add_argument('outdir', help='Output directory.')
    parser.add_argument('det', choices=['i', 's'], help='Detector.')
    parser.add_argument('subdet', type=int, choices=list(range(10)), help='Subdetector.')
    
    args = parser.parse_args()
    mk_stats(args.indir, args.outdir,  args.det, args.subdet)

if __name__ == '__main__':
    main()
