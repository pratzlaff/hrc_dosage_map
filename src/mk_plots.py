import argparse
import os
import re
import string
import sys

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

import HRCExp

plt.rcParams['axes.titley'] = 1.0    # y is in axes-relative coordinates.
plt.rcParams['axes.titlepad'] = -14  # pad is in points...

import HRCExp

def mk_plots(sdir, outdir):

    HRCExp.mkdir_p(outdir)

    for det in HRCExp.dets():
        for i in range(HRCExp.nsubdets(det)):

            ofile = f'{outdir}/hrc{det}{i}.png'

            cdata =  HRCExp.read_stat_file(sdir, det, i, 'c')
            mdata =  HRCExp.read_stat_file(sdir, det, i, 'm')

            plot_hrc_dose(cdata, mdata, ofile)

def plot_hrc_dose(cdata, mdata, ofile):

    date = cdata[0]+(cdata[1]-0.5)/12
    x = date

    ax1 = plt.subplot(3,2,1)
    y = mdata[2]
    plt.plot(x, y, lw=1, marker='+', markersize=1.5)
    plt.title('Average')

    ax2 = plt.subplot(3,2,2)
    y = cdata[2]
    plt.plot(x, y, lw=1, marker='+', markersize=1.5)
    plt.title('Cumulative Average')

    ax3 = plt.subplot(3,2,3)
    y = mdata[6]
    plt.plot(x, y, lw=1, marker='+', markersize=1.5)
    plt.title('Maximum')


    ax4 = plt.subplot(3,2,4)
    y = cdata[6]
    plt.plot(x, y, lw=1, marker='+', markersize=1.5)
    plt.title('Maximum Cumulative')

    labels = ["68% Value ", "95% Value", "99.7% Value"]

    ax5 = plt.subplot(3,2,5)
    for i in range(3):
        y = mdata[8+i]
        plt.plot(x, y, '-', label=labels[i])
    legend(loc='upper left')

    ax6 = plt.subplot(3,2,6)
    for i in range(3):
        y = cdata[8+i]
        plt.plot(x, y, '-', label=labels[i])
    legend(loc='upper left')

    for ax in ax1, ax2, ax3, ax4, ax5, ax6:
        if ax != ax5 and ax != ax6:
            for label in ax.get_xticklabels():
                label.set_visible(False)
        else:
            pass
        ax3.set_ylabel('Counts per Pixel')
        ax5.set_xlabel('Year')
        ax6.set_xlabel('Year')

    fig = plt.gcf()
    fig.set_size_inches(10.0, 10.0)

    plt.tight_layout()
    plt.savefig(ofile, format='png', dpi=200)

    plt.close()

def main():
    parser = argparse.ArgumentParser(
        description='Create plots of exposure statistics.'
    )
    parser.add_argument('sdir', help='Statistics directory.')
    parser.add_argument('outdir', help='Output directory.')
    args = parser.parse_args()

    mk_plots(args.sdir, args.outdir)

if __name__ == '__main__':
    main()
