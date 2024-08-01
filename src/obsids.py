import argparse

import HRCExp

def obsids(i=True, s=True)
    pass

def main():
    parser = argparse.ArgumentParser(
        description='Print HRC obsids.' 
    )
    parser.add_argument('--i', action='store_const', default=True, const=True, dest='i')
    parser.add_argument('--no-i', action='store_const', const=False, dest='i')
    parser.add_argument('--s', action='store_const', default=True, const=True, dest='i')
    parser.add_argument('--no-s', action='store_const', const=False, dest='i')
    args = parser.parse_args()
    print(args)
    obsids(args.i, args.s)

if __name__ == '__main__':
    main()

