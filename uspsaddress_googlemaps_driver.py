"""
To standardize address in samplefordatalinkage.csv using Google Maps API on the first two records:

  $ time python uspsaddress_googlemaps_driver.py --n 2 --m 3

To standardize address in samplefordatalinkage.csv with noise:

  $ time python uspsaddress_googlemaps_driver.py --n 2 --m 3 --g 1

To time, use "time" utility on unix and adds up USER + SYS time:

  $ time python uspsaddress_googlemaps_driver.py --n 2 --m 3 --g 1

"""

import argparse
import random
import time

t0 = time.clock()

parser = argparse.ArgumentParser()
parser.add_argument('--n', '--number_of_records', type=int, default=2500, help='number of records', metavar='n')
parser.add_argument('--m', '--method of choice', type=int, default=6, help="""
                            method of choice:
                            1-3: for Google Maps APIs;
                            4: Geocoder.us;
                            5: Data Science Toolkit;
                            6: usaddress.""", metavar='m')
parser.add_argument('--g', '--generate noise', type=int, default=0, help="1: to generate noise", metavar='g')

args = parser.parse_args()
n=args.n
m=args.m
g=args.g

print "n = %s, m = %s, g = %s" % (n,m,g)

from uspsaddress_googlemaps import uspsaddress_googlemaps

usadd = uspsaddress_googlemaps()
random.seed(0) # for reproducibility
if m>=1 and m<=3:
  usadd.eval_googlemaps(n,m,g)
elif m==4:
  usadd.eval_geocoder_us(n,g)
elif m==5:
  usadd.eval_data_science_toolkit(n,g)
elif m==6:
  usadd.eval_usaddress(n,g)

print "\ncpu time = ", time.clock()-t0