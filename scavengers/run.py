# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Author: tabara.mihai@gmail.com (Mihai Tabara)

"""
Flickr non-null response: camp101988@yahoo.com
Jigsaw non-null response: asadat@salesforce.com
"""

import sys, flickr, jigsaw, google_plus, github, myspace

func_dict = {
              "FLICKR" : flickr.flickr,
              "JIGSAW" : jigsaw.jigsaw,
              "GOOGLE+" : google_plus.google_plus,
              "GITHUB" : github.github,
              "MySpace" : myspace.myspace
            }

def print_result(result, email, network):
  print 'Results for %s email address in %s network:' % (email, network)

  if result is None:
    print 'Username not found'
  else:
    print result

  print

def run_scavangers(emails):
  for email in emails:
    for key in func_dict:
      result = func_dict[key](email)
      print_result(result, email, key)

if __name__=="__main__":
  if len(sys.argv) > 1:
    run_scavangers(sys.argv[1:])
  else:
    print 'usage: run.py <input_email1> <input_email2> ...'
