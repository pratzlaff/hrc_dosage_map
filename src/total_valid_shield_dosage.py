import argparse
import astropy.io.fits
import glob
import sys

import HRCDose

def get_detnam(obsid):
    try:
        bpix1 = glob.glob(f'/data/hrc/[is]/{obsid}/secondary/*bpix1.fits*')[0]
    except:
        return None
    with astropy.io.fits.open(bpix1) as hdulist:
        return hdulist['badpix'].header['detnam']

def read_dosage(obsid):
    try:
        ss0 = glob.glob(f'/data/hrc/[is]/{obsid}/hk/*ss0.fits*')
    except:
        return None

    counts = { 'total':0,
               'valid':0,
               'shield':0,
              }

    for f in ss0:
        with astropy.io.fits.open(f) as hdulist:
            data = hdulist['sscience'].data
            counts['total'] += data['tlevart'].sum()
            counts['valid'] += data['vlevart'].sum()
            counts['shield'] += data['shevart'].sum()
        
    return counts

def total_valid_shield_dosage(args):
    obsids = [f'{o:05d}' for o in HRCDose.year_month_obsids_archive(args.year, args.month)]
    #obsids=['00132', '01200', '01201', '01202', '01203', '01204', '01205', '01206', '01207', '01208', '01209', '01210', '01282', '01283', '01284', '01285', '01286', '01287', '01288', '01289', '01294', '01295', '01296', '62446', '62448', '62449', '62937', '62948', '62956', '62986']
    counts = { 'HRC-I':{ 'total':0, 'valid':0, 'shield':0},
               'HRC-S':{ 'total':0, 'valid':0, 'shield':0} }

    for obsid in obsids:
        detnam = get_detnam(obsid)
        #sys.stderr.write(f'{obsid}: {detnam}\n')
        if detnam is None:
            sys.stderr.write(f'could not read DETNAM for ObsID {obsid}\n')
            continue
        counts_o = read_dosage(obsid)
        if counts_o is None:
            sys.stderr.write(f'could not read counts for ObsID {obsid}\n')
            continue
        for k in counts_o:
            counts[detnam][k] += counts_o[k]
        
    print('\t'.join([str(args.year),
	      str(args.month),
	      str(counts['HRC-I']['total']),
	      str(counts['HRC-I']['valid']),
	      str(counts['HRC-I']['shield']),
	      str(counts['HRC-S']['total']),
	      str(counts['HRC-S']['valid']),
	      str(counts['HRC-S']['shield'])
	     ]))
    
def main():
    parser = argparse.ArgumentParser(
        description='Compute HRC Total/Valid/Shield events for a given year and month.'
    )
    parser.add_argument('year', type=int, choices=range(1999,2027))
    parser.add_argument('month', type=int, choices=range(1,13))
    args = parser.parse_args()
    total_valid_shield_dosage(args)

if __name__ == '__main__':
  main()
