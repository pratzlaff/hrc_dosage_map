import argparse
import glob
import sys

def obsids_by_month_dets(args):
    print('\t'.join(['Year', 'Month', 'ObsIDs_I', 'Obsids_S']))

    for line in sys.stdin:
        year, month, obsids = line.split('\t')
        obsids = obsids.rstrip()
        obsids_i = []
        obsids_s = []

        for obsid in obsids.split(','):
            if not len(obsids):
                continue
            count = 0
            globstr = f'/data/hrc/i/{obsid}/secondary/hrcf{obsid}*bpix1.fits*'
            bpix = glob.glob(globstr)
            count += len(bpix)
            if bpix:
                obsids_i.append(obsid)
            globstr = f'/data/hrc/s/{obsid}/secondary/hrcf{obsid}*bpix1.fits*'
            bpix = glob.glob(globstr)
            count += len(bpix)
            if bpix:
                obsids_s.append(obsid)
            if not count:
                raise RuntimeError(f'{count} bpix files found for ObsID {obsid}')
        print('\t'.join([year, month, ','.join(obsids_i), ','.join(obsids_s)]))

def main():
    parser = argparse.ArgumentParser(
        description='Given input containing year, month, and comma-separated list of ObsIDs, split into I and S columns.'
    )
    args = parser.parse_args()
    obsids_by_month_dets(args)

if __name__ == '__main__':
  main()
