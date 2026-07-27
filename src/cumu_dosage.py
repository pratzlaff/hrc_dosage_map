import argparse
import numpy as np
import sys

def cumu_dosage(args):
    print('\t'.join(['Year', 'Month', 'I', 'S', 'I_cumu', 'S_cumu']))

    year, month, i, s1, s2, s3 = np.loadtxt(sys.stdin, dtype=int, unpack=True)
    np.savetxt(sys.stdout, np.column_stack([year, month, i, (s1+s2+s3), np.cumsum(i), np.cumsum(s1+s2+s3) ]), fmt='%.4g')

    

def main():
    parser = argparse.ArgumentParser(
        description='Compute HRC cumulative dosage.'
    )
    args = parser.parse_args()
    cumu_dosage(args)

if __name__ == '__main__':
  main()
