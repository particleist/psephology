import os,sys
import array
from math import *
import shelve
import argparse
from helpers import niceprint,getmargin,printmarginal
from helpers import nicepartynames

# Basic analysis scripts, may get factored in the near future. Comments
# explaining what each script does can be found within it.

parser = argparse.ArgumentParser(description='Some basic analysis scripts')
parser.add_argument('--debug', dest='debug', action='store_true',
                    help='Turn on debug mode')
parser.add_argument('--marginals', dest='marginals', action='store', nargs = 2, type = str,
                    help='Print out the list of marginals for a given year. If you want to know the\
                          marginals going into the 1997 election, you should run the script for 1992.\
                          Of course this doesn\'t account for boundary changes but those make marginals\
                          a bit tricky to define anyhow. \
                          The correct input format is \'year percentage\', for example\
                          \'1997 5.0\'.')
parser.add_argument('--marginals_between', dest='marginals_between', action='store', nargs = 4, type = str,
                    help='Print out the list of marginals for a given year between two parties. If you want to know the\
                          marginals going into the 1997 election, you should run the script for 1992.\
                          The first party is the one holiding the seat, the second is the challenger.\
                          Of course this doesn\'t account for boundary changes but those make marginals\
                          a bit tricky to define anyhow. \
                          The correct input format is \'holder challenger year percentage\', for example\
                          \'Conservative Labour 1992 5.0\'.')
parser.add_argument('--input', dest='input', action='store',
                    default = '../data/dbase/results',
                    help='Set the name of the input file, defaults to ../data/dbase/results')

args = parser.parse_args()

try :
  outputdatabase = shelve.open(args.input)
except :
  print 'No shelve database found at the given location, exiting'
  sys.exit(0)

def marginals(year, cutoff) :
  # This is a simple analysis which prints out the list of marginals after each
  # election. I.e. if you would like to know which seats were marginals going into
  # 1997, modulo boundary changes, ask for the marginals after 1992. The analysis
  # can be given a cutoff for what you would like to consider a marginal
  print
  print '------------------------------------------------------------'
  print 'Retreiving marginals below',cutoff+"%",'for',year
  print '------------------------------------------------------------'
  print
  seats = []
  for constituency in outputdatabase :
    # First, does it exist in the given year? 
    if not outputdatabase[constituency].has_key(year) : 
      continue
    else :
      thismargin = getmargin(constituency,year,outputdatabase)
      if 100.0 * thismargin < float(cutoff):
        seats.append((thismargin,constituency))
  seats.sort()
  for seat in seats :
    printmarginal(seat[1],year,outputdatabase)
  print
  print '------------------------------------------------------------'
  print 'Finished printout of',len(seats),'marginals below',cutoff+"%",'for',year
  print '------------------------------------------------------------'
  print
  return

def marginals_between(party1, party2, year, cutoff) :
  # This is a simple analysis which prints out the list of marginals after each
  # election which party1 holds with respect to party2. I.e. if you would like to
  # know which seats were Tory-Labour marginals (held by Tories) going into
  # 1997, modulo boundary changes, ask for the marginals after 1992. The analysis
  # can be given a cutoff for what you would like to consider a marginal
  print
  print '------------------------------------------------------------'
  print 'Retreiving',party1+'-'+party2,'marginals below',cutoff+"%",'for',year
  print '------------------------------------------------------------'
  print
  seats = []
  for constituency in outputdatabase :
    # First, does it exist in the given year? 
    if not outputdatabase[constituency].has_key(year) : 
      continue
    else :
      if not nicepartynames(party1) == nicepartynames(outputdatabase[constituency][year]["winner"]["party"]) :
        continue
      if not nicepartynames(party2) == nicepartynames(outputdatabase[constituency][year]["second"]["party"]) :
        continue
      thismargin = getmargin(constituency,year,outputdatabase)
      if 100.0 * thismargin < float(cutoff):
        seats.append((thismargin,constituency))
  seats.sort()
  for seat in seats :
    printmarginal(seat[1],year,outputdatabase)
  print
  print '------------------------------------------------------------'
  print 'Finished printout of',len(seats),party1+'-'+party2,'marginals below',cutoff+"%",'for',year
  print '------------------------------------------------------------'
  print
  return

if args.marginals : 
  year = args.marginals[0]
  cutoff = args.marginals[1]
  marginals(year,cutoff)
if args.marginals_between :
  party1 = args.marginals_between[0]
  party2 = args.marginals_between[1]
  year   = args.marginals_between[2]
  cutoff = args.marginals_between[3]
  marginals_between(party1,party2,year,cutoff)

