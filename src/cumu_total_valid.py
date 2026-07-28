import argparse
import numpy as np
import sys

def cumu_total_valid(args):
    print('\t'.join(['Year', 'Month', 'I_total', 'I_valid', 'I_shield', 'I_total_cumu', 'I_valid_cumu', 'I_shield_cumu', 'S_total', 'S_valid', 'S_shield', 'S_total_cumu', 'S_valid_cumu', 'S_shield_cumu']))

    year, month, t_i, v_i, s_i, t_s, v_s, s_s = np.loadtxt(sys.stdin, dtype=int, unpack=True)
    np.savetxt(sys.stdout, np.column_stack([year, month, t_i, v_i, s_i, np.cumsum(t_i), np.cumsum(v_i), np.cumsum(s_i), t_s, v_s, s_s, np.cumsum(t_s), np.cumsum(v_s), np.cumsum(s_s)]), fmt='%.4g', delimiter='\t')

def main():
    parser = argparse.ArgumentParser(
        description='Compute HRC Total/Valid/Shield events for a given year and month.'
    )
    args = parser.parse_args()
    cumu_total_valid(args)

if __name__ == '__main__':
  main()
