import os,sys
import array
from math import *
import shelve
import argparse
from helpers import nicepartynames

parser = argparse.ArgumentParser(description='Scipt which builds the DB of election results')
parser.add_argument('--debug', dest='debug', action='store_true',
                    help='Turn on debug mode')
parser.add_argument('--output', dest='output', action='store',
                    default = '../data/dbase/results',
                    help='Set the name of the output file, defaults to ../data/dbase/results')

args = parser.parse_args()

# This script processes the csv files in the data/csv directory and creates
# a single python dictionary/database which contains the information relevant
# for the analysis. This data is then output to the data/dbase directory.
#
# The output data format is a shelve database, with a dictionary structure
# as defined below. At present no self-documenting versioning of the
# writing/reading scripts is implemented, but they should always be in sync
# in the head of the repository.

'''
The constituencies are a dictionary with the constituency name as a key.
Each constituency is itself a dictionary, whose key is the election year.
Both these dictionary keys are strings.

Each constitutency only has entries for those years for which it existed.

Each result is accessed by using the year as a key, and contains

WINNER , VOTES : PAIR OF (STRING,INT)
SECOND PLACE , VOTES : PAIR OF (STRING,INT)
ELECTORATE : INT 
TURNOUT : DOUBLE

This data format is optimized for following the evolution of constituencies
as a function of time while minimizing duplication of data and hence the
database size. Other methods of indexing are of course possible. 
'''

def storeoneentry(outputdatabase,constituency,year,winner,runnerups,electorate,turnout) :
  # We have all the information now, so fill the dictionary
  # the copy malarkey is to avoid having to use shelve with the
  # writeback option set to true
  if not outputdatabase.has_key(constituency) :
    outputdatabase[constituency] = {year : {} }
  else :
    copy = outputdatabase[constituency]
    copy[year] = {}
    outputdatabase[constituency] = copy
  copy = outputdatabase[constituency]
  copy[year]["winner"]     = winner
  copy[year]["second"]     = runnerups[0]
  copy[year]["third"]      = runnerups[1]
  copy[year]["electorate"] = electorate
  copy[year]["turnout"]    = turnout
  outputdatabase[constituency] = copy

csv_file_prefix = "../data/csv/"
csv_file_suffix  = ".csv"

try :
  outputdatabase = shelve.open(args.output)
except :
  print 'Cannot create shelve database at the given location, exiting'
  sys.exit(0)

# Note that because the csv file format is different for different years,
# we will need to implement several reading loops. Let's begin
# with the 1992-2001 data which is in (almost) the same format.

for year in ['1992','1997','2001'] :
  print "I am now processing the",year,"data"
  # open the file
  filetoread = open(csv_file_prefix + year + csv_file_suffix, 'r')
  # define the variables used to store a single result
  # There is probably a smarter way to handle all the shelve
  # persistency malarkey...
  foundconstituency = False
  constituency = ""
  winner = {"party" : "", "vote" : 0}
  runnerups = [{"party" : "", "vote" : 0},{"party" : "", "vote" : 0}]
  electorate = 0
  turnout = 0.0
  for line in filetoread : 
    if not foundconstituency :
      runnerup = 0         
      # Find the start of a new constituency result
      # We look for Hold/Gain strings late in the line
      if line.find(' Hold') > 30 or line.find(' Gain') > 30 : 
        resultfirstline = line.split(',')
        if args.debug : print resultfirstline
        constituency = resultfirstline[0].rstrip('"').lstrip('"')
        winner["party"] = nicepartynames(resultfirstline[3])
        winner["vote"] = int(resultfirstline[4])
        electorate = int(resultfirstline[6])
        turnout = float(resultfirstline[8].rstrip('%'))
        foundconstituency = True
      continue
    # If we got this far we are adding a new constituency result
    resultsecondline = line.split(',')
    if args.debug : print resultsecondline    
    runnerups[runnerup]["party"] = nicepartynames(resultsecondline[3])
    runnerups[runnerup]["vote"] = int(resultsecondline[4])
    storeoneentry(outputdatabase,constituency,year,winner,runnerups,electorate,turnout)
 
    runnerup += 1
    if runnerup > 1 :
      foundconstituency = False    
 
  filetoread.close()

# Now 2005/2010, which is in another format
for year in ['2005','2010'] :
  print "I am now processing the",year,"data"
  # open the file
  filetoread = open(csv_file_prefix + year + csv_file_suffix, 'r')
  # define the variables used to store a single result
  # There is probably a smarter way to handle all the shelve
  # persistency malarkey...
  foundconstituency = False
  constituency = ""
  winner = {"party" : "", "vote" : 0}
  runnerups = [{"party" : "", "vote" : 0},{"party" : "", "vote" : 0}]
  electorate = 0
  turnout = 0.0
  for line in filetoread : 
    if not foundconstituency :  
      runnerup = 0 
      # Find the start of a new constituency result
      # We look for [, which seems to demarcate the constituency number here 
      if line.find('[') > -1 : 
        resultfirstline = line.split(',')
        if args.debug : print resultfirstline
        constituency = (resultfirstline[0].rstrip('"').lstrip('"')).split('[')[0].strip()    
        if year == '2005' :
          winner["party"] = nicepartynames(resultfirstline[4])
          winner["vote"] = int(resultfirstline[5].replace("'",""))
          turnout = float(resultfirstline[1])
        else : 
          winner["party"] = nicepartynames(resultfirstline[5])
          winner["vote"] = int(resultfirstline[6].replace("'",""))
          turnout = float(resultfirstline[2])
          electorate = int(resultfirstline[1].replace("'",""))              
        foundconstituency = True
      continue
    # If we got this far we are adding a new constituency result
    resultsecondline = line.split(',')
    if args.debug : print resultsecondline   
    if year == '2005' and runnerups == 0: 
      electorate = int(resultsecondline[0].replace("'",""))    
    runnerups[runnerup]["party"] = nicepartynames(resultsecondline[4])
    runnerups[runnerup]["vote"] = int(resultsecondline[5].replace("'",""))
    storeoneentry(outputdatabase,constituency,year,winner,runnerups,electorate,turnout)
 
    runnerup += 1
    if runnerup > 1 :
      foundconstituency = False    
 
  filetoread.close()

# Now 2015 which is in yet another format
for year in ['2015'] :
  print "I am now processing the",year,"data"
  # open the file
  filetoread = open(csv_file_prefix + year + csv_file_suffix, 'r')
  # define the variables used to store a single result
  # There is probably a smarter way to handle all the shelve
  # persistency malarkey...
  constituency = ""
  winner = {"party" : "", "vote" : 0}
  runnerups = [{"party" : "", "vote" : 0},{"party" : "", "vote" : 0}]
  electorate = 0
  turnout = 0.0
  partyorder = ["Con","Lab","LD","SNP","PC","UKIP","Green","BNP"] 
  for line in filetoread :
    # just skip the first line
    if args.debug : print 'Skipping first line in 2015 file for bookkeeping'
    break
  for line in filetoread :  
    # In this file all the data is on a single line
    resultline = line.split(',')
    if args.debug : print resultline
    constituency = (resultline[0].rstrip('"').lstrip('"')).split('[')[0].strip()    
    turnout = float(resultline[2])    
    electorate = int(resultline[-1])    
    counter = 3
    votes = []    
    for party in partyorder :
      thisvote = 0
      if resultline[counter] == '' : 
        thisvote = 0
      else : 
        thisvote = int(resultline[counter])
      votes.append( ( thisvote , party ) )
      counter += 1
    votes.sort()
    votes.reverse()
    if args.debug : print votes
    winner["party"] = nicepartynames(votes[0][1])
    winner["vote"]  = votes[0][0]
    for runnerup in [0,1] :
      runnerups[runnerup]["party"] = nicepartynames(votes[runnerup+1][1])
      runnerups[runnerup]["vote"]  = votes[runnerup+1][0]
    storeoneentry(outputdatabase,constituency,year,winner,runnerups,electorate,turnout)
 
  filetoread.close()

# If in debug mode, let's print the result out! 
if args.debug : 
  for constituency in outputdatabase :
    print constituency
    print outputdatabase[constituency]
    print

# Store the list of years available in the database, in order
outputdatabase["elections"] = [1992,1997,2001,2005,2010,2015]
outputdatabase.close()
