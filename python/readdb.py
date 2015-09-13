import os,sys
import array
from math import *
import shelve
import argparse
from helpers import niceprint

parser = argparse.ArgumentParser(description='An example script to read back the results database')
parser.add_argument('--debug', dest='debug', action='store_true',
                    help='Turn on debug mode')
parser.add_argument('--fullprint', dest='fullprint', action='store_true',
                    help='Print out the full database in a nice format')
parser.add_argument('--print', dest='constituency', action='store',
                    default = "",
                    help='Print out the entries for a constituency')
parser.add_argument('--input', dest='input', action='store',
                    default = '../data/dbase/results',
                    help='Set the name of the input file, defaults to ../data/dbase/results')

args = parser.parse_args()

# This is a simple example script to read back and dump the database written
# by the builddb script. It also lets you print the results for a single constituency
# for all the years in order.

outputdatabase = shelve.open(args.input)

# Let's print the result out in a nice way! 
if args.constituency != "" : 
  if outputdatabase.has_key(args.constituency) :
    niceprint(args.constituency,outputdatabase)
  else :  
    print
    print 'The constituency you requested does not exist in the database'
    print 'As the database is derived from electoral commission data, it'
    print 'may be that the name is simply in a different format to the'
    print 'one you expected. Here is the alphabetical list of all the'
    print 'constituencies which I know about.'
    print 
    keys = []
    for key in outputdatabase :
      keys.append(key)
    keys.sort()
    for key in keys : print key
#
if args.fullprint :
  for constituency in outputdatabase :
    niceprint(constituency,outputdatabase)
