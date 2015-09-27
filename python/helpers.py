import os,sys
import array
from math import *

# Shared helper functions for the the main scripts

def nicepartynames(name) :
  # Defines the uniform party names (the ones on the right hand side) used
  # to translate the multitude of names in the input csv files.
  #
  # NOTE : Labour/Cooperative is reduced to Labour here. While it loses
  #        some information, this is done because in the very latest
  #        results (i.e. 2015) the electoral commission dropped the
  #        distinction, so it cannot help present day analysis. 
  #
  nicename = { 
               "Lab"                                       : "Labour",
               "Labour"                                    : "Labour",
               "Labour/Co-operative"                       : "Labour",
               "Labour Co-op"                              : "Labour",
               "Independent Labour"                        : "Independent Labour",
               "Socialist Labour"                          : "SLP",
               "SL"                                        : "SLP",
               "SLP"                                       : "SLP",
               "Con"                                       : "Conservative",
               "Conservative"                              : "Conservative",
               "Tory"                                      : "Conservative",
               "LD"                                        : "Lib Dem",
               "Liberal Democrat"                          : "Lib Dem",
               "Lib Dem"                                   : "Lib Dem",
               "Scottish National"                         : "SNP",
               "SNP"                                       : "SNP",
               "Ulster Unionist"                           : "Ulster Unionist",
               "UUP"                                       : "Ulster Unionist",
               "Democratic Unionist"                       : "DUP",
               "DUP"                                       : "DUP",
               "Social Democratic and Labour"              : "SDLP",
               "SDLP"                                      : "SDLP",
               "Alliance"                                  : "Alliance",
               'APNI'                                      : 'Alliance',
               "Sinn F\x8ein"                              : "Sinn Fein",
               "SF"                                        : "Sinn Fein",
               "Sinn Fein"                                 : "Sinn Fein",
               'Plaid Cymru'                               : "Plaid Cymru",
               'PC'                                        : "Plaid Cymru",
               'Ulster Unionist'                           : 'Ulster Unionist',         
               'UU'                                        : 'Ulster Unionist',                   
               'Ulster Popular Unionist'                   : 'Ulster Popular Unionist',
               'Progressive Unionist'                      : 'Progressive Unionist',
               'Scottish Militant Labour'                  : 'Scottish Militant Labour',
               'Social Democrat'                           : 'SDP',
               'SDP'                                       : 'SDP',
               'United Kingdom Unionist'                   : 'United Kingdom Unionist',
               'Lib'                                       : 'Liberal',
               'Liberal'                                   : 'Liberal',
               'Independent'                               : 'Independent',
               'Ind'                                       : 'Independent',
               'Speaker'                                   : 'The Speaker',               
               'The Speaker'                               : 'The Speaker',
               'Kidderminster Hospital and Health Concern' : 'KHHC',
               'KHHC'                                      : 'KHHC',
               'Scottish Socialist Alliance'               : 'Scottish Socialist Alliance',
               'Resp'                                      : 'Respect',
               'Respect'                                   : 'Respect',
               'BG'                                        : 'Blaenau Gwent',
               'BGPV'                                      : 'Blaenau Gwent',
               'Blaenau Gwent'                             : 'Blaenau Gwent',
               'UCUNF'                                     : 'UCUNF',
               'TUV'                                       : 'TUV',
               'GRN'                                       : 'Green',
               'Grn'                                       : 'Green',
               'Green'                                     : 'Green',
               'ISGB'                                      : 'ISGB',
               'ICHC'                                      : 'ICHC',
               'BNP'                                       : 'BNP',
               'British National'                          : 'BNP',
               'UKIP'                                      : 'UKIP',
               'National Democratic Resistance'            : 'National Democratic Resistance',
               "Women's Coalition (NI)"                    : "Women's Coalition (NI)",
               'Chairman of Sunrise Radio'                 : 'Chairman of Sunrise Radio',
               'Scottish Socialist'                        : 'SSP',
               'SSP'                                       : 'SSP',
               'Socialist Alliance'                        : 'Socialist Alliance',
               'SA'                                        : 'Socialist Alliance',
               "People's Justice"                          : "People's Justice Party",
               "People's Justice Party"                    : "People's Justice Party" 
             }
  return nicename[name]

def niceprint(constituency,outputdatabase,printorder = ["winner","second","third","electorate","turnout"]) :
  # Prints out the full result for a single constituency, for all years of existence
  print constituency,":"
  years = []
  for year in outputdatabase[constituency] :
    years.append(year)
  years.sort()
  for year in years :
    print "  ",year,":"
    for data in printorder :
      if type(outputdatabase[constituency][year][data]) == dict :
        print "    ","{:<10}".format(data),":","{:<20}".format(outputdatabase[constituency][year][data]["party"]),outputdatabase[constituency][year][data]["vote"]
      else :
        print "    ","{:<10}".format(data),":",outputdatabase[constituency][year][data]

def getmargin(constituency,year,outputdatabase) :
  # Get the winning margin for one constituency in a given year
  totalvoters = int(outputdatabase[constituency][year]["electorate"])*float(outputdatabase[constituency][year]["turnout"])/100.0
  margin = 0.5*(float(outputdatabase[constituency][year]["winner"]["vote"]) - 
            float(outputdatabase[constituency][year]["second"]["vote"]) )/totalvoters
  return margin 

def getmarginbtwparties(constituency,year,party1,party2,outputdatabase) :
  # Get the margin for one constituency in a given year between a given two parties
  totalvoters = int(outputdatabase[constituency][year]["electorate"])*float(outputdatabase[constituency][year]["turnout"])/100.0
  parties_in_year = {}
  for result in possibleresults() :
    parties_in_year[outputdatabase[constituency][year][result]["party"]] = outputdatabase[constituency][year][result]["vote"]
  if not (parties_in_year.has_key(party1) and parties_in_year.has_key(party2)) :
    return 1.0
  margin = 0.5*(float(parties_in_year[party1]) - float(parties_in_year[party2]) )/totalvoters
  return margin 

def printmarginal(constituency,year,outputdatabase) :
  # Prints out a single constitutency for a given year, winner, runner up, margin
  print "{:<45}".format(constituency),\
        "{:<30}".format(outputdatabase[constituency][year]["winner"]["party"]+' --- '+\
                        outputdatabase[constituency][year]["second"]["party"]),\
        "{:.2%}".format(getmargin(constituency,year,outputdatabase))

def possibleresults() :
  return ["winner","second","third"]
