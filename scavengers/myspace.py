# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

from scavenger_utils import http_request

MYSPACE_HOST = "api.myspace.com"
MYSPACE_PATH = "/opensearch/people/"

def myspace(email):
  params = {
              'searchTerms' : email,
              'searchBy' : 'email',
              'format' : 'json'
           }
  response = http_request("GET", MYSPACE_HOST, MYSPACE_PATH, params)
  if response.status == 404:
    return ""
# TODO (Diana) parse response
  return response.read()

if __name__=="__main__":
  print myspace("dia_tiriplica@yahoo.co.uk")
  print myspace("diana.tiriplica@gmail.com")
