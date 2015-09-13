import os,sys
import array
from math import *

# Shared helper functions for the the main scripts

def nicepartynames(name) :
  nicename = { 
               "Lab"                                       : "Labour",
               "Labour"                                    : "Labour",
               "Labour/Co-operative"                       : "Labour_coop",
               "Labour Co-op"                              : "Labour_coop",
               "Con"                                       : "Conservative",
               "Conservative"                              : "Conservative",
               "LD"                                        : "Lib Dem",
               "Liberal Democrat"                          : "Lib Dem",
               "Scottish National"                         : "SNP",
               "SNP"                                       : "SNP",
               "Ulster Unionist"                           : "Ulster Unionist",
               "UUP"                                       : "Ulster Unionist",
               "Democratic Unionist"                       : "Democratic Unionist",
               "DUP"                                       : "Democratic Unionist",
               "Social Democratic and Labour"              : "SDLP",
               "SDLP"                                      : "SDLP",
               "Alliance"                                  : "Alliance",
               'APNI'                                      : 'Alliance',
               "Sinn F\x8ein"                              : "Sinn Fein",
               "SF"                                        : "Sinn Fein",
               'Plaid Cymru'                               : "Plaid Cymru",
               'PC'                                        : "Plaid Cymru",
               'Ulster Unionist'                           : 'Ulster Unionist',         
               'UU'                                        : 'Ulster Unionist',                   
               'Ulster Popular Unionist'                   : 'Ulster Popular Unionist',
               'Scottish Militant Labour'                  : 'Scottish Militant Labour',
               'Social Democrat'                           : 'SDP',
               'United Kingdom Unionist'                   : 'United Kingdom Unionist',
               'Liberal'                                   : 'Liberal',
               'Independent'                               : 'Independent',
               'Ind'                                       : 'Independent',
               'Speaker'                                   : 'The Speaker',               
               'The Speaker'                               : 'The Speaker',
               'Kidderminster Hospital and Health Concern' : 'Kidderminster Hospital and Health Concern',
               'KHHC'                                      : 'Kidderminster Hospital and Health Concern',
               'Resp'                                      : 'Respect',
               'Respect'                                   : 'Respect',
               'BG'                                        : 'Blaenau Gwent',
               'BGPV'                                      : 'Blaenau Gwent',
               'UCUNF'                                     : 'UCUNF',
               'TUV'                                       : 'TUV',
               'GRN'                                       : 'Green',
               'Green'                                     : 'Green',
               'ISGB'                                      : 'ISGB',
               'ICHC'                                      : 'ICHC',
               'BNP'                                       : 'BNP',
               'UKIP'                                      : 'UKIP'
             }
  return nicename[name]

def niceprint(constituency,outputdatabase,printorder = ["winner","second","electorate","turnout"]) :
  print constituency,":"
  years = []
  for year in outputdatabase[constituency] :
    years.append(year)
  years.sort()
  for year in years :
    print "  ",year,":"
    for data in printorder :
      print "    ",data,":",outputdatabase[constituency][year][data]
