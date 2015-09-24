import os,sys
import array
from math import *
import shelve
import argparse
from helpers import niceprint,getmargin,printmarginal
from helpers import nicepartynames,possibleresults

# Basic analysis scripts, may get factored in the near future. Comments
# explaining what each script does can be found within it.

parser = argparse.ArgumentParser(description='Some basic analysis scripts')
parser.add_argument('--debug', dest='debug', action='store_true',
                    help='Turn on debug mode')
parser.add_argument('--marginals', dest='marginals', metavar = ('Year','Percentage'), action='store', nargs = 2, type = str,
                    help='Print out the list of marginals for a given year. If you want to know the\
                          marginals going into the 1997 election, you should run the script for 1992.\
                          Of course this doesn\'t account for boundary changes but those make marginals\
                          a bit tricky to define anyhow. \
                          The correct input format is \'year percentage\', for example\
                          \'1997 5.0\'.')
parser.add_argument('--marginals_between', dest='marginals_between', metavar = ('Holder', 'Challenger', 'Year', 'Percentage'), action='store', nargs = 4, type = str,
                    help='Print out the list of marginals for a given year between two parties. If you want to know the\
                          marginals going into the 1997 election, you should run the script for 1992.\
                          The first party is the one holiding the seat, the second is the challenger.\
                          Of course this doesn\'t account for boundary changes but those make marginals\
                          a bit tricky to define anyhow. \
                          The correct input format is \'holder challenger year percentage\', for example\
                          \'Conservative Labour 1992 5.0\'.')
parser.add_argument('--swing', dest='swing', action='store', metavar = ('Party-from','Party-to','Year'), nargs = 3, type = str,
                    help='Print out the swing between two parties, by seat, for a given election. The\
                          swing is calculated with respect to the previous election. The correct input\
                          format is \'party party year\', for example \'Tory Labour 1997\'. Note that\
                          the swing is FROM the first party TO the second, while negative values indicate swings\
                          from second to first. Only seats contested in both elections count.')
parser.add_argument('--gainbyparty', dest='gainbyparty', metavar = ('Party','Year'), action='store', nargs = 2, type = str,
                    help='Print out the number of votes gained by a party, by seat, for a given election. The\
                          gain is calculated with respect to the previous election. The correct input\
                          format is \'party year\', for example \'Labour 1997\'. Note that\
                          negative values indicate a loss of votes. Only seats contested in both elections count.')
parser.add_argument('--input', dest='input', action='store',metavar = 'Input-database',
                    default = '../data/dbase/results',
                    help='Set the name of the input file, defaults to ../data/dbase/results')

args = parser.parse_args()

try :
  outputdatabase = shelve.open(args.input)
except :
  print 'No shelve database found at the given location, exiting'
  sys.exit(0)

def marginals(year, cutoff, printout = True) :
  # This is a simple analysis which prints out the list of marginals after each
  # election. I.e. if you would like to know which seats were marginals going into
  # 1997, modulo boundary changes, ask for the marginals after 1992. The analysis
  # can be given a cutoff for what you would like to consider a marginal
  if printout :
    print
    print '------------------------------------------------------------'
    print 'Retreiving marginals below',cutoff+"%",'for',year
    print '------------------------------------------------------------'
    print
  seats = []
  for constituency in outputdatabase :
    if constituency == "elections" : continue    
    # First, does it exist in the given year? 
    if not outputdatabase[constituency].has_key(year) : 
      continue
    else :
      thismargin = getmargin(constituency,year,outputdatabase)
      if 100.0 * thismargin < float(cutoff):
        seats.append((thismargin,constituency))
  seats.sort()
  if printout :
    for seat in seats :
      printmarginal(seat[1],year,outputdatabase)
  if printout :
    print
    print '------------------------------------------------------------'
    print 'Finished printout of',len(seats),'marginals below',cutoff+"%",'for',year
    print '------------------------------------------------------------'
    print
  return seats

def marginals_between(party1, party2, year, cutoff, printout = True) :
  # This is a simple analysis which prints out the list of marginals after each
  # election which party1 holds with respect to party2. I.e. if you would like to
  # know which seats were Tory-Labour marginals (held by Tories) going into
  # 1997, modulo boundary changes, ask for the marginals after 1992. The analysis
  # can be given a cutoff for what you would like to consider a marginal
  if printout :
    print
    print '------------------------------------------------------------'
    print 'Retreiving',party1+'-'+party2,'marginals below',cutoff+"%",'for',year
    print '------------------------------------------------------------'
    print
  seats = []
  for constituency in outputdatabase :
    if constituency == "elections" : continue    
    # First, does it exist in the given year? 
    if not outputdatabase[constituency].has_key(year) : 
      continue
    else :
      if not party1 == outputdatabase[constituency][year]["winner"]["party"] :
        continue
      if not party2 == outputdatabase[constituency][year]["second"]["party"] :
        continue
      thismargin = getmargin(constituency,year,outputdatabase)
      if 100.0 * thismargin < float(cutoff):
        seats.append((thismargin,constituency))
  seats.sort()
  if printout :
    for seat in seats :
      printmarginal(seat[1],year,outputdatabase)
  if printout :
    print
    print '------------------------------------------------------------'
    print 'Finished printout of',len(seats),party1+'-'+party2,'marginals below',cutoff+"%",'for',year
    print '------------------------------------------------------------'
    print
  return seats

def gainbyparty(party, year, printout = True) :
  # This analysis prints an ordered list of votes gained by a party in a given
  # election, with respect to the previous election. Only seats contested in both
  # elections are counted. 
  #
  # Get the previous election year
  if printout :
    print
    print '--------------------------------------------------------------------------------------------------------------------------------------------------------'
    print 'Starting printout of votes gained by',party,'in',year
    print '--------------------------------------------------------------------------------------------------------------------------------------------------------'
    print
  #
  former_year = str(outputdatabase["elections"][outputdatabase["elections"].index(int(year))-1])
  year = str(year)
  if args.debug : print former_year, year
  votegains = []
  alsoin2015 = 0
  totalvotegain = 0
  votegaininsafe2015 = 0
  for constituency in outputdatabase :
    if constituency == "elections" : continue    
    # Was it contested in both elections?
    if not (outputdatabase[constituency].has_key(former_year) and \
            outputdatabase[constituency].has_key(year) ) :
      continue 
    # OK they did, carry on now
    if args.debug : 
      niceprint(constituency,outputdatabase)
    party_scores = []
    # This loop works because a party only has one entry per seat per year
    for election in [former_year,year] :
      for result in possibleresults() :
        if party == outputdatabase[constituency][election][result]["party"] :
          party_scores.append(outputdatabase[constituency][election][result]["vote"])
    if not len(party_scores) == 2 : continue
    # The votes gaines
    thisgain_abs = party_scores[1]-party_scores[0]
    # The percentage majority at the previous election
    thismajority = getmargin(constituency,year,outputdatabase)
    formermajority = getmargin(constituency,former_year,outputdatabase)
    votegains.append((thisgain_abs,thismajority,formermajority,constituency,
                      outputdatabase[constituency][year]["winner"]["party"],
                      outputdatabase[constituency][former_year]["winner"]["party"]))
    totalvotegain += thisgain_abs  
    if outputdatabase[constituency].has_key('2015') : 
      alsoin2015 += 1 
      if outputdatabase[constituency]['2015']["winner"]["party"] == party :
        votegaininsafe2015 += thisgain_abs
  #
  # Now print it out
  #
  votegains.sort()
  if printout :
    print '--------------------------------------------------------------------------------------------------------------------------------------------------------'
    print "{:<35}".format("Constituency"), "{:^20}".format("Votes Gained"), "{:^20}".format(str(year)+" winner"), "{:^20}".format(str(year)+" majority"), "{:^20}".format(str(former_year)+" winner"), "{:^20}".format(str(former_year)+" majority")
    print '--------------------------------------------------------------------------------------------------------------------------------------------------------'
    for votegain in votegains :
      print "{:40}".format(votegain[3]),"{:>8}".format(votegain[0]), "{:>21}".format(votegain[4]), "{:>19.2%}".format(votegain[1]), "{:>21}".format(votegain[5]), "{:>19.2%}".format(votegain[2])
    #
    print
    print 'There were',len(votegains),'contituencies in common between the',year,'and',former_year,'elections'
    print alsoin2015,'of these also existed in the 2015 election'
    print 'The overall vote gain for',party,'in',year,"was",totalvotegain
    print 'The overall vote gain in seats',party,'still holds in 2015 was',votegaininsafe2015
    print
    print '--------------------------------------------------------------------------------------------------------------------------------------------------------'
    print 'Finished printout of votes gained by',party,'in',year
    print '--------------------------------------------------------------------------------------------------------------------------------------------------------'
    print
  return votegains


def swing(party1, party2, year, printout = True) :
  # This analysis prints an ordered list of swings from party1 to party2 in a given
  # election, with respect to the previous election. Only seats contested in both
  # elections are counted. 
  #
  # The swing is defined as half the change between the score differences of the parties
  # from the first election to the second one
  #
  # Get the previous election year
  if printout :
    print
    print '-------------------------------------------------------------------------------------------------'
    print 'Starting printout of swings from',party1,"to",party2,'in',year
    print '-------------------------------------------------------------------------------------------------'
    print
  #
  former_year = str(outputdatabase["elections"][outputdatabase["elections"].index(int(year))-1])
  year = str(year)
  if args.debug : print former_year, year
  swings = []
  for constituency in outputdatabase :
    if constituency == "elections" : continue    
    # Was it contested in both elections?
    if not (outputdatabase[constituency].has_key(year)        and \
            outputdatabase[constituency].has_key(former_year) ) :
      continue
    # Have to see if the parties both contested the constituency in both elections
    passedchecks = True
    for election in [former_year,year] :
      parties_in_year = []
      for result in possibleresults() :
        parties_in_year.append(outputdatabase[constituency][election][result]["party"])
      if not (party1 in parties_in_year and party2 in parties_in_year) :
        passedchecks = False
    if not passedchecks : continue
    # OK they did, carry on now
    if args.debug : 
      niceprint(constituency,outputdatabase)
    party1_scores = []
    party2_scores = []
    # This loop works because each party only has one entry per seat per year
    for election in [former_year,year] :
      for result in possibleresults() :
        if party1 == outputdatabase[constituency][election][result]["party"] :
          party1_scores.append(outputdatabase[constituency][election][result]["vote"])
        elif party2 == outputdatabase[constituency][election][result]["party"] :
          party2_scores.append(outputdatabase[constituency][election][result]["vote"])       
    # The percentage swing
    if args.debug : print constituency, outputdatabase[constituency][year]
    thisswing = 100.0*(party2_scores[1]-party1_scores[1])/(outputdatabase[constituency][year]["electorate"]*outputdatabase[constituency][year]["turnout"]) - \
                100.0*(party2_scores[0]-party1_scores[0])/(outputdatabase[constituency][former_year]["electorate"]*outputdatabase[constituency][former_year]["turnout"])
    # The absolute swing
    thisswing_abs = (party2_scores[1]-party1_scores[1]) - (party2_scores[0]-party1_scores[0])
    # The percentage majority at the previous election
    thismajority = 100.0*(party2_scores[0]-party1_scores[0])/(outputdatabase[constituency][former_year]["electorate"]*outputdatabase[constituency][former_year]["turnout"])
    swings.append((thisswing/2.,thisswing_abs/2.,thismajority,constituency))
  #
  # Now print it out
  #
  swings.sort()
  if printout :
    totalvoteswing = 0
    avgpercswing   = 0
    print '-------------------------------------------------------------------------------------------------'
    print "{:<35}".format("Constituency"), "{:^20}".format("Percentage swing"), "{:^20}".format("Absolute swing"), "{:^20}".format(str(year)+" majority")
    print '-------------------------------------------------------------------------------------------------'
    for swing in swings :
      print "{:40}".format(swing[3]),"{:>8.2%}".format(swing[0]), "{:>21}".format(swing[1]), "{:>19.2%}".format(swing[2])
      totalvoteswing += swing[1]
      avgpercswing   += swing[0]
    #
    avgpercswing /= len(swings)
    print
    print 'The average swing from',party1,"to",party2,'in',year,"was","{:0.2%}".format(avgpercswing)
    print 'The overall vote swing from',party1,"to",party2,'in',year,"was",totalvoteswing
    print
    print '-------------------------------------------------------------------------------------------------'
    print 'Finished printout of swings from',party1,"to",party2,'in',year
    print '-------------------------------------------------------------------------------------------------'
    print
  return swings

if args.marginals : 
  year = args.marginals[0]
  cutoff = args.marginals[1]

  if str(year) not in str(outputdatabase["elections"]) :
    print "You have asked for a non-existent year, exiting now"
    sys.exit(1)

  marginals(year,cutoff)
#
if args.marginals_between :
  party1 = nicepartynames(args.marginals_between[0])
  party2 = nicepartynames(args.marginals_between[1])
  year   = args.marginals_between[2]
  cutoff = args.marginals_between[3]

  if str(year) not in str(outputdatabase["elections"]) :
    print "You have asked for a non-existent year, exiting now"
    sys.exit(1)

  marginals_between(party1,party2,year,cutoff)
#
if args.swing :
  party1 = nicepartynames(args.swing[0])
  party2 = nicepartynames(args.swing[1])
  year   = int(args.swing[2])

  if year not in outputdatabase["elections"] :
    print "You have asked for a non-existent year, exiting now"
    sys.exit(1)
  if year == outputdatabase["elections"][0] :
    print "I do not have information about the election before",year,"exiting now"
    sys.exit(1)
 
  swing(party1,party2,year)
#
if args.gainbyparty :
  party = nicepartynames(args.gainbyparty[0])
  year   = int(args.gainbyparty[1])

  if year not in outputdatabase["elections"] :
    print "You have asked for a non-existent year, exiting now"
    sys.exit(1)
  if year == outputdatabase["elections"][0] :
    print "I do not have information about the election before",year,"exiting now"
    sys.exit(1)
 
  gainbyparty(party,year)
