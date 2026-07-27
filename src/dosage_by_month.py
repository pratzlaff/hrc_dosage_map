import argparse
import astropy.io.fits as fits

def dosage_by_month(args):
    ids = { 'HRC-I':'i0',
            'HRC-S1':'s0',
            'HRC-S2':'s1',
            'HRC-S3':'s2'
           }
    sums = []
    for id in ids:
        f = f'/data/hrc/DoseMaps/monthly/hrc{ids[id]}m_{args.year}-{args.month:02d}.fits.gz'
        with fits.open(f) as hdulist:
            sums.append(hdulist[0].data.sum())
    print('\t'.join([str(x) for x in [args.year,args.month]+sums]))

def main():
    parser = argparse.ArgumentParser(
        description='Sum HRC dosage maps for a given month.'
    )
    parser.add_argument('year', type=int)
    parser.add_argument('month', type=int)
    args = parser.parse_args()
    dosage_by_month(args)

if __name__ == '__main__':
  main()
