# Copyright 2012 Droopy @Sunnytrail Insight Labs Inc. All rights reserved
# Author: tabara.mihai@gmail.com (Mihai Tabara)

# Flickr scavenger: gathers any type of personal data around an email address
# from Flickr social network

# The scanvanger receives a job consisting an email address and returns a result
# of a JSON format. (None if user not found) within 2 API calls
# Example of fields returned:
# http://api.flickr.com/services/rest/?method=flickr.people.getInfo&api_key=
# d75138bb5caa8f70bb5b3dc071e19e6e&user_id=9910681@N02

import simplejson as json
from scavenger_utils import http_request

FLICKR_HOST = "api.flickr.com"
FLICKR_PATH = "/services/rest/"

FLICKR_KEY = 'd75138bb5caa8f70bb5b3dc071e19e6e'
FLICKR_PWD = '1e7edafa40c76873'

def flickr(email):
  """
  TODO(Mihai): find a better and cleaner solution.
  The Flickr API retrieves something like 'jsonFlickrApi({..})'.
  One solution would've been the use of urllib.urlopen instead of http_request.
  However, I chose to substring the {..} part and convert it to json.
  """
  queries = {
              "email" : "flickr.people.findByEmail",
              "user" : "flickr.people.getInfo"
            }

  params = {
              "method" : queries['email'],
              "api_key" : FLICKR_KEY,
              "find_email" : email,
              "format" : "json"
           }

  response = http_request("GET", FLICKR_HOST, FLICKR_PATH, params)
  message = response.read()
  message = message[14:len(message)-1]
  data = json.loads(message)

  if data['stat'] == 'fail':
    return None

  user_id = data['user']['id']

  params['method'] = queries['user']
  params['user_id'] = str(user_id)
  del params['find_email']

  response = http_request("GET", FLICKR_HOST, FLICKR_PATH, params)
  message = response.read()
  message = message[14:len(message)-1]

  return json.loads(message)
