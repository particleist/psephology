import os,sys
import array
from math import *
import shelve
import argparse
from helpers import niceprint,getmargin,printmarginal
from helpers import nicepartynames,possibleresults,getmarginbtwparties
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size': 15})

# Basic analysis scripts, may get factored in the near future. Comments
# explaining what each script does can be found within it.

parser = argparse.ArgumentParser(description='Some basic analysis scripts')
parser.add_argument('--debug', dest='debug', action='store_true',
                    help='Turn on debug mode')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    help='Turn on verbose mode')
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
parser.add_argument('--boundarychanges', dest='boundarychanges', metavar = ('Year-1','Year-2'), action='store', nargs = 2, type = str,
                    help='Nicely print the seats which changed between two years. The correct input\
                          format is \'year-1 year-2\', for example \'2001 2015\'.')
parser.add_argument('--blairslostvotes', dest='blairslostvotes', action='store_true',
                    help='Perform analysis of electoral utility of the votes Tony Blair lost Labour\
                          in the 2001 and 2005 elections.')
parser.add_argument('--progvsreactalliance', dest='progvsreactalliance', metavar = ('year'), action='store', nargs = 1, type = str,
                    help='Perform analysis of electoral utility of a progressive (Lab-LD-Green) vs. reactionary (Con-UKIP) alliance.')
parser.add_argument('--partyrisevsturnout', dest='partyrisevsturnout', metavar = ('party','year'), action='store', nargs = 2, type = str,
                    help='Plot votes gained by party vs. increase in seat turnout for a given year')
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
      if args.verbose :
        niceprint(seat[1],outputdatabase,yeartoprint=year)
        print
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
      if args.verbose :
        niceprint(seat[1],outputdatabase,yeartoprint=year)
        print
  if printout :
    print
    print '------------------------------------------------------------'
    print 'Finished printout of',len(seats),party1+'-'+party2,'marginals below',cutoff+"%",'for',year
    print '------------------------------------------------------------'
    print
  return seats

def gainbyparty(party, year, former_year = -999, printout = True) :
  # This analysis prints an ordered list of votes gained by a party in a given
  # election, with respect to the previous election. Only seats contested in both
  # elections are counted. At the end, a small printout is also made of the overall
  # totals, and the relevance of these votes to the 2015 picture in the seats 
  #
  # Get the previous election year
  if printout :
    print
    print '--------------------------------------------------------------------------------------------------------------------------------------------------------'
    print 'Starting printout of votes gained by',party,'in',year
    print '--------------------------------------------------------------------------------------------------------------------------------------------------------'
    print
  #
  if former_year == -999 :
    former_year = str(outputdatabase["elections"][outputdatabase["elections"].index(int(year))-1])
  year = str(year)
  former_year = str(former_year)
  if args.debug : print former_year, year
  votegains = []
  alsoin2015 = 0
  totalvotegain = 0
  votegainsin2015 = { "Labour" : [], "Conservative" : [], "Lib Dem" : []}
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
      for winner2015 in ['Labour','Conservative','Lib Dem'] : 
        if outputdatabase[constituency]['2015']["winner"]["party"] in [winner2015] :
          votegainsin2015[winner2015].append(thisgain_abs)
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
    for winner2015 in ['Labour','Conservative','Lib Dem'] : 
      print 'The overall vote gain in the',len(votegainsin2015[winner2015]),'seats which the',winner2015,'party still holds in 2015 was',sum(votegainsin2015[winner2015])
    print
    print '--------------------------------------------------------------------------------------------------------------------------------------------------------'
    print 'Finished printout of votes gained by',party,'in',year
    print '--------------------------------------------------------------------------------------------------------------------------------------------------------'
    print
  return alsoin2015,totalvotegain,votegainsin2015,votegains

def swing(party1, party2, year, former_year = -999, printout = True) :
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
  if former_year == -999 :
    former_year = str(outputdatabase["elections"][outputdatabase["elections"].index(int(year))-1])
  year = str(year)
  former_year = str(former_year)
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
    print "{:<35}".format("Constituency"), "{:^20}".format("Percentage swing"), "{:^20}".format("Absolute swing"), "{:^20}".format(str(former_year)+" majority")
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

def boundarychanges(year1,year2, printout = True) :
  # Nicely print out the seats which only existed in each of the two input years, side by side
  if printout :
    print
    print '------------------------------------------------------------'
    print 'Printing the boundary changes between',year1,'and',year2
    print '------------------------------------------------------------'
    print
    print "{:50}".format("Only in "+year1),"{:50}".format("Only in "+year2)
    print '------------------------------------------------------------'
  onlyinyear1 = []
  onlyinyear2 = []
  for constituency in outputdatabase :
    if constituency == "elections" : continue    
    if   (not outputdatabase[constituency].has_key(year1)) and \
             (outputdatabase[constituency].has_key(year2)) :
      onlyinyear2.append(constituency)
    elif (not outputdatabase[constituency].has_key(year2)) and \
             (outputdatabase[constituency].has_key(year1)) :
      onlyinyear1.append(constituency)
  #
  # Begin the printout
  onlyinyear1.sort()
  onlyinyear2.sort()
  for i,constituency in enumerate(onlyinyear1) :
    toprint = "{:50}".format(onlyinyear1[i]) + " " 
    if (i < len(onlyinyear2) ) :
      toprint += "{:50}".format(onlyinyear2[i])
    print toprint
  #
  if printout :
    print
    print '------------------------------------------------------------'
    print 'Finished printing the boundary changes between',year1,'and',year2
    print '------------------------------------------------------------'
    print
  return onlyinyear1,onlyinyear2

def blairslostvotes() :
  # Perform an analysis of the votes lost by Tony Blair in the 2001
  # and 2005 elections and estimate the electoral utility of regaining them
  # in 2020. Doesn't account for possible boundary changes after 2015.
  alsoin2015,totalvoteloss,votelossin2015,voteloss_labour_2005 = gainbyparty('Labour',2005,1997,printout=False)
  print 'There were',len(voteloss_labour_2005),'contituencies in common between the 2005 and 1997 elections'
  print alsoin2015,'of these also existed in the 2015 election'
  print 'The overall votes lost by Blair by 2005 were',totalvoteloss
  for winner2015 in ['Labour','Conservative','Lib Dem'] : 
    print 'The overall votes lost in the',len(votelossin2015[winner2015]),'seats which the',winner2015,'party still holds in 2015 were',sum(votelossin2015[winner2015])
  # OK this is the big picture, now how many of these votes are in useful Tory seats?
  lostvotes = []
  margin = []
  seatsvulnerabletolostvoters = 0
  print
  print 'Beginning printout of vote losses by Tory-held 2015 seat'
  print
  for constituency in voteloss_labour_2005 :
    constituency_name = constituency[3]
    if not outputdatabase[constituency_name].has_key('2015') :
      continue
    if outputdatabase[constituency_name]['2015']["winner"]["party"] != "Conservative" : 
      continue
    constituency_margin = getmarginbtwparties(constituency_name,'2015','Conservative','Labour',outputdatabase)
    print "{:50}".format(constituency_name),"{:0.2%}".format(constituency_margin),"{:15}".format(constituency[0])
    if constituency_margin < 1.0 :
      margin.append(100.0*constituency_margin)
      lostvotes.append(constituency[0])
      if 2.*constituency_margin\
           *float(outputdatabase[constituency_name]["2015"]["electorate"])\
           *float(outputdatabase[constituency_name]["2015"]["turnout"])/100.0\
         <\
         -1.*float(constituency[0]) :
        seatsvulnerabletolostvoters += 1
  print 
  print 'In total',seatsvulnerabletolostvoters,'could be won by gaining the votes lost by Blair'
  print
  # Plot the lost votes
  plt.scatter(lostvotes,margin)
  plt.xlabel('Blair\'s lost votes')
  plt.ylabel('Percentage gap Tory-Labour in 2015')
  plt.show()
  return 1

def progvsreactalliance(year='2015') :
  # Perform an analysis of Tory-Labour marginals if 80% of 2015 UKIP votes go to Tories 
  # while 80% of LD and Green votes go to Labour
  marginals = {}
  marginals["Conservative-Labour"] = marginals_between('Conservative','Labour', year, 30.0, printout = False)
  marginals["Conservative-Lib Dem"]  = marginals_between('Conservative','Lib Dem', year, 30.0, printout = False)
  marginals["Labour-Conservative"] = marginals_between('Labour', 'Conservative', year, 30.0, printout = False)
  margins = []
  abstentions    = []
  shiftedmargins = []
  shiftinmargins = []
  for partyorder in ["Conservative-Labour","Conservative-Lib Dem","Labour-Conservative"] :
    p1 = partyorder.split('-')[0]
    p2 = partyorder.split('-')[1]
    margin = []
    abstention    = []
    shiftedmargin = []
    shiftinmargin = []
    for constituency in marginals[partyorder] :
      constituency_name = constituency[1]
      totalvoters = int(outputdatabase[constituency_name][year]["electorate"])
      abstention.append(totalvoters*(100.0-outputdatabase[constituency_name][year]["turnout"])/100.0)
      if outputdatabase[constituency_name][year]["winner"]["party"] == "Conservative" :
        convoters = outputdatabase[constituency_name][year]["winner"]["vote"]
        labvoters = outputdatabase[constituency_name][year]["second"]["vote"]
      else :
        convoters = outputdatabase[constituency_name][year]["second"]["vote"]
        labvoters = outputdatabase[constituency_name][year]["winner"]["vote"]
      constituency_margin = 0.5*(convoters - labvoters)/totalvoters
      # Now add third/fourth place 
      for result in ["third","fourth"] : 
        if outputdatabase[constituency_name][year][result]["party"] in ['Conservative','UKIP'] : 
          convoters += 0.8 * outputdatabase[constituency_name][year][result]["vote"]
        elif outputdatabase[constituency_name][year][result]["party"] in ['Labour','Lib Dem','Green'] :
          labvoters += 0.8 * outputdatabase[constituency_name][year][result]["vote"]
      # Recompute the constituency margin now
      constituency_margin_shifted = 0.5*(convoters - labvoters)/totalvoters
      margin.append(100.0*constituency_margin)
      shiftedmargin.append(2.0*constituency_margin_shifted*totalvoters)
      shiftinmargin.append(100.0*(constituency_margin_shifted-constituency_margin))
   
      print "{:50}".format(constituency_name),"{:0.2%}".format(constituency_margin),"   ",\
            "{:0.2%}".format(constituency_margin_shifted),"    ","{:0.2f}".format(outputdatabase[constituency_name][year]["turnout"])
    margins.append(margin)
    abstentions.append(abstention)
    shiftedmargins.append(shiftedmargin)
    shiftinmargins.append(shiftinmargin)
  # Plot the lost votes
  x = range(-1,1)
  y = range(-1,1)
  fig = plt.figure("Margin vs. shift")
  ax1 = fig.add_subplot(111)

  ax1.scatter(margins[0],shiftinmargins[0],c='r',marker = "s",label='Con-Lab')
  ax1.scatter(margins[1],shiftinmargins[1],c='b',marker = "o",label='Con-LD')
  ax1.scatter(margins[2],shiftinmargins[2],c='g',marker = "d",label='Lab-Con')
  plt.xlabel('Con-Lab/LD margin '+year+' (%)')
  plt.ylabel('Shift towards Con (%)')
  plt.legend(loc='lower right')
  plt.plot((-25, 25), (0, 0), 'k--', lw = 3.0)
  plt.xlim(-25,25)
  plt.show()

  fig2 = plt.figure("Shifted margin vs. abstention")
  ax2 = fig2.add_subplot(111)
  ax2.scatter(abstentions[0],shiftedmargins[0],c='r',marker = "s",label='Con-Lab')  
  ax2.scatter(abstentions[1],shiftedmargins[1],c='b',marker = "o",label='Con-LD')  
  ax2.scatter(abstentions[2],shiftedmargins[2],c='g',marker = "d",label='Lab-Con')  
  plt.xlabel('Non-voters in '+year)
  plt.ylabel('Con lead in seat')
  plt.legend(loc='lower left')
  plt.plot((0, 40000), (0, 40000), 'k--', lw = 3.0)
  plt.plot((0, 160000), (0, 80000), 'k-.', lw = 3.0)
  plt.plot((0, 160000), (0, 40000), 'k:', lw = 3.0)
  plt.xlim(10000,40000)
  plt.ylim(-60000,50000)
  plt.show()

  return 1

def partyrisevsturnout(party='Labour',year='2017') :
  # Perform an analysis of how much a party's vote has increased in a given constituency compared to the 
  # number of extra voters in that constituency since the last election
  former_year = str(outputdatabase["elections"][outputdatabase["elections"].index(int(year))-1])
  year = str(year)
  if args.debug : print former_year, year
  party_gain = []
  total_gain = []
  party_winning_gain = []
  total_winning_gain = []
  registered_increase = []
  registered_winning_increase = []
  turnout_increase = []
  turnout_winning_increase = []
  party_majority_prev_5kplus = []
  party_majority_prev_2kplus = []
  party_majority_prev_0kplus = []
  total_gain_in_5kplus = []
  total_gain_in_2kplus = []
  total_gain_in_0kplus = []
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
    total_votes  = []
    total_registered = [] 
    total_turnout = []
    # This loop works because a party only has one entry per seat per year
    for election in [former_year,year] :
      for result in possibleresults() :
        if party == outputdatabase[constituency][election][result]["party"] :
          party_scores.append(outputdatabase[constituency][election][result]["vote"])
          total_votes.append(int(outputdatabase[constituency][election]["electorate"]*outputdatabase[constituency][election]["turnout"]/100.0))
          total_registered.append(int(outputdatabase[constituency][election]["electorate"]))
          total_turnout.append(int(outputdatabase[constituency][election]["turnout"]))
 
    if not len(party_scores) == 2     : continue
    if not len(total_votes)  == 2     : continue
    if not len(total_registered) == 2 : continue
    if not len(total_turnout) == 2 : continue

    this_gain = party_scores[1]-party_scores[0]
    this_total_gain = total_votes[1]-total_votes[0]
    this_registered_increase = total_registered[1]-total_registered[0]
    this_turnout_increase = total_turnout[1]-total_turnout[0]
    this_party_majority_prev = 0
    if (party == outputdatabase[constituency][former_year]["winner"]["party"]) :
      this_party_majority_prev = +1.*(outputdatabase[constituency][former_year]["winner"]["vote"]-outputdatabase[constituency][former_year]["second"]["vote"])
    elif (party == outputdatabase[constituency][former_year]["second"]["party"]) :     
      this_party_majority_prev = -1.*(outputdatabase[constituency][former_year]["winner"]["vote"]-outputdatabase[constituency][former_year]["second"]["vote"])
    elif (party == outputdatabase[constituency][former_year]["third"]["party"]) :     
      this_party_majority_prev = -1.*(outputdatabase[constituency][former_year]["winner"]["vote"]-outputdatabase[constituency][former_year]["third"]["vote"])
    elif (party == outputdatabase[constituency][former_year]["fourth"]["party"]) :     
      this_party_majority_prev = -1.*(outputdatabase[constituency][former_year]["winner"]["vote"]-outputdatabase[constituency][former_year]["fourth"]["vote"])
    else :
      this_party_majority_prev = -9999999999. # default value shouldn't come up for big parties

    if (party == outputdatabase[constituency][year]["winner"]["party"]) and \
       not (party == outputdatabase[constituency][former_year]["winner"]["party"]) :
      party_winning_gain.append(this_gain)
      total_winning_gain.append(this_total_gain) 
      registered_winning_increase.append(this_registered_increase)
      turnout_winning_increase.append(this_turnout_increase)
    else : 
      party_gain.append(this_gain)
      total_gain.append(this_total_gain)
      registered_increase.append(this_registered_increase)
      turnout_increase.append(this_turnout_increase)
    
    if this_total_gain > 5000 :
      party_majority_prev_5kplus.append(this_party_majority_prev)
      total_gain_in_5kplus.append(this_total_gain)      
    elif this_total_gain > 2000 :
      party_majority_prev_2kplus.append(this_party_majority_prev)
      total_gain_in_2kplus.append(this_total_gain)    
    elif this_total_gain > 0 :        
      party_majority_prev_0kplus.append(this_party_majority_prev)
      total_gain_in_0kplus.append(this_total_gain)    

  fig = plt.figure("Extra voters for"+party+" vs. increase in total votes")
  ax1 = fig.add_subplot(111)
  ax1.scatter(party_gain,total_gain,c='w',s=36,marker = "s",label = 'All seats')
  ax1.scatter(party_winning_gain,total_winning_gain,c='r',s=36,marker = "s",label=party+' gains')
  plt.xlabel(party+' votes gained in '+year)
  plt.ylabel('Extra voters in '+year)
  plt.legend(loc='lower right')
  plt.xlim(-9000,16000)
  plt.ylim(-9000,9000)
  plt.show()

  fig2 = plt.figure("Increase in overall vote vs. previous party lead in seat")
  ax2 = fig2.add_subplot(111)
  ax2.scatter(party_majority_prev_5kplus,total_gain_in_5kplus,c='r',marker = "s",label='>5k extra votes')  
  ax2.scatter(party_majority_prev_2kplus,total_gain_in_2kplus,c='b',marker = "o",label='>2k extra votes')  
  ax2.scatter(party_majority_prev_0kplus,total_gain_in_0kplus,c='g',marker = "d",label='>0  extra votes')  
  plt.xlabel(party+' lead in '+former_year)
  plt.ylabel('Extra votes in '+year)
  plt.legend(loc='upper left')
  plt.plot((0, 0), (0, 20000), 'k--', lw = 2.0)
  plt.xlim(-20000,20000)
  plt.ylim(0,10000)
  plt.show()

  fig3 = plt.figure("Extra voters for"+party+" vs. increase in registered voters")
  ax3 = fig3.add_subplot(111)
  ax3.scatter(party_gain,registered_increase,c='w',s=36,marker = "s",label = 'All seats')
  ax3.scatter(party_winning_gain,registered_winning_increase,c='r',s=36,marker = "s",label=party+' gains')
  plt.xlabel(party+' votes gained in '+year)
  plt.ylabel('Extra registrations in '+year)
  plt.legend(loc='upper left')
  plt.xlim(-9000,16000)
  plt.ylim(-9000,9000)
  plt.show()

  fig4 = plt.figure("Extra voters for"+party+" vs. increase in % turnout")
  ax4 = fig4.add_subplot(111)
  ax4.scatter(party_gain,turnout_increase,c='w',s=36,marker = "s",label = 'All seats')
  ax4.scatter(party_winning_gain,turnout_winning_increase,c='r',s=36,marker = "s",label=party+' gains')
  plt.xlabel(party+' votes gained in '+year)
  plt.ylabel('% turnout increase in '+year)
  plt.legend(loc='upper left')
  plt.xlim(-9000,16000)
  plt.ylim(-10,17.5)
  plt.show()

  return 1


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
if args.boundarychanges :
  year1 = args.boundarychanges[0]
  year2 = args.boundarychanges[1]
  if int(year1) not in outputdatabase["elections"] or int(year2) not in outputdatabase["elections"] :
    print "You have asked for a non-existent year, exiting now"
    sys.exit(1)
  boundarychanges(year1,year2)
#
if args.blairslostvotes :
  blairslostvotes()

if args.progvsreactalliance :
  progvsreactalliance(args.progvsreactalliance[0])

if args.partyrisevsturnout :
  partyrisevsturnout(nicepartynames(args.partyrisevsturnout[0]),args.partyrisevsturnout[1])


