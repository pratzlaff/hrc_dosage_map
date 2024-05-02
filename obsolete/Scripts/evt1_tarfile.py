import argparse
import glob
import os
import subprocess
import sys

import HRCExp

def evt1_tarfile(year, month):

    obsids, dets = HRCExp.year_month_obsids(year, month)
    if not obsids.size:
        sys.stderr.write("no obsids found\n")
        sys.exit(0)

    tar_args = ['tar', 'cvf', f'evt1_{year}_{month:02d}.tar']
    for i in range(obsids.size):
        f = glob.glob(f'/data/hrc/*/{obsids[i]:05d}/secondary/*evt1.fits*')
        if f:
            tar_args.append(f[-1])
        else:
            sys.stderr.write(f'no EVT1 files found for obsid {obsids[i]:05d}\n')

    print(tar_args)
    subprocess.run(tar_args)

def main():
    parser = argparse.ArgumentParser(
        description='Create tar file containing evt1 files for a given year/month.',
    )
    parser.add_argument('year', type=int)
    parser.add_argument('month', type=int)
    args = parser.parse_args()
    evt1_tarfile(args.year, args.month)

if __name__ == '__main__':
    main()
