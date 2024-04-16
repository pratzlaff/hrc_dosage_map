import argparse
import subprocess
import sys

import HRCExp

def evt1_tarfile(year, month):

    obsids, dets = HRCExp.year_month_obsids(year, month)
    if not obsids.size:
        sys.stderr.write("no obsids found\n")
        sys.exit(0)

    files_i = [f'/data/hrc/i/{o:05d}/secondary/*evt1.fits*' for o in obsids[dets=='HRC-I']]
    files_s = [f'/data/hrc/s/{o:05d}/secondary/*evt1.fits*' for o in obsids[dets=='HRC-S']]

    files = [*files_i, *files_s]

    tarfile = f'evt1_{year}_{month:02d}.tar'
    tar_args = ['tar', 'cvf', tarfile, *files]
    subprocess.run(tar_args, shell=True)

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
