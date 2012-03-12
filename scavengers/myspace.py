# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

# This scavenger gets information about a user from MySpace.

import simplejson
from scavenger_utils import http_request

MYSPACE_HOST = "api.myspace.com"
MYSPACE_PATH = "/opensearch/people/"

def myspace(email):
  params = {
              'searchTerms' : email,
              'searchBy' : 'email',
              'format' : 'json'
           }
  response = http_request(email, "GET", MYSPACE_HOST, MYSPACE_PATH, params)

  if response.is_error():
    return response

# Information useful: displayname, age, gender, location
  return simplejson.loads(response['raw_data'])

if __name__=="__main__":
  data = myspace("dia_tiriplica@yahoo.co.uk")
  for k in data:
    print k, data[k]
