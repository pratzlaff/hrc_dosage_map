import argparse
import sys

def cumu_total_valid(args):
    print('\t'.join(['Year', 'Month', 'I_total', 'I_valid', 'I_shield', 'I_total_cumu', 'I_valid_cumu', 'I_shield_cumu', 'S_total', 'S_valid', 'S_shield', 'S_total_cumu', 'S_valid_cumu', 'S_shield_cumu']))

    ct_i, cv_i, cs_i, ct_s, cv_s, cs_s = 0, 0, 0, 0, 0, 0
    for line in sys.stdin:
        year, month, t_i, v_i, s_i, t_s, v_s, s_s = line.split('\t')

        t_i = int(t_i)
        v_i = int(v_i)
        s_i = int(s_i)
        t_s = int(t_s)
        v_s = int(v_s)
        s_s = int(s_s)

        ct_i += t_i
        cv_i += v_i
        cs_i += s_i
        ct_s += t_s
        cv_s += v_s
        cs_s += s_s

        print('\t'.join([str(year),
                         str(month),
                         f'{t_i:.4g}',
                         f'{v_i:.4g}',
                         f'{s_i:.4g}',
                         f'{ct_i:.4g}',
                         f'{cv_i:.4g}',
                         f'{cs_i:.4g}',
                         f'{t_s:.4g}',
                         f'{v_s:.4g}',
                         f'{s_s:.4g}',
                         f'{ct_s:.4g}',
                         f'{cv_s:.4g}',
                         f'{cs_s:.4g}',
                         ]))

def main():
    parser = argparse.ArgumentParser(
        description='Compute HRC Total/Valid/Shield events for a given year and month.'
    )
    args = parser.parse_args()
    cumu_total_valid(args)

if __name__ == '__main__':
  main()
