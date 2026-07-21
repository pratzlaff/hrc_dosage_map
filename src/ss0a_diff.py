import argparse
import astropy.io.fits

def time_minmax(fits):
    with astropy.io.fits.open(fits) as hdulist:
        time = hdulist['sscience'].data['time']
        tmin, tmax = time.min(), time.max()
        return tmin, tmax

def ss0_diff(args):
    ss0a_tmin, ss0a_tmax = time_minmax(args.ss0a)
    ss0_tmin, ss0_tmax = time_minmax(args.ss0)

    print(f'ss0a spans {ss0a_tmax-ss0a_tmin:.0f} seconds, begins {ss0a_tmin-ss0_tmin:.0f} seconds after ss0, and ends {ss0_tmax-ss0a_tmax:.0f} seconds before.')

def main():
    parser = argparse.ArgumentParser(
        description='Compare ss0a and ss0 times.'
    )
    parser.add_argument('ss0a')
    parser.add_argument('ss0')
    args = parser.parse_args()
    ss0_diff(args)

if __name__ == '__main__':
  main()
