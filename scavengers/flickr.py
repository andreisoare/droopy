# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Author: tabara.mihai@gmail.com (Mihai Tabara)

# Flickr scavenger: gathers any type of personal data around an email address
# from Flickr social network

# The scanvanger receives a job consisting an email address and returns a result
# of a JSON format. (None if user not found) within 2 API calls
# Example of fields returned:
# http://api.flickr.com/services/rest/?method=flickr.people.getInfo&api_key=
# d75138bb5caa8f70bb5b3dc071e19e6e&user_id=9910681@N02

import simplejson
from scavenger_utils import http_request

FLICKR_HOST = "api.flickr.com"
FLICKR_PATH = "/services/rest/"

FLICKR_KEY = 'd75138bb5caa8f70bb5b3dc071e19e6e'
FLICKR_PWD = '1e7edafa40c76873'
RESPONSE_PREFIX_LENGTH = 14

def flickr(email):
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

  response = http_request(email, "GET", FLICKR_HOST, FLICKR_PATH, params)
  if response.is_error():
    return response
  message = response['raw_data']
  # Jump over the first 14 characters and get the actual JSON
  message = message[RESPONSE_PREFIX_LENGTH:len(message)-1]
  data = simplejson.loads(message)
  if data['stat'] == 'fail':
    return None

  user_id = data['user']['id']

  params['method'] = queries['user']
  params['user_id'] = str(user_id)
  del params['find_email']

  response = http_request(email, "GET", FLICKR_HOST, FLICKR_PATH, params)
  message = response['raw_data']
  message = message[RESPONSE_PREFIX_LENGTH:len(message)-1]

  return simplejson.loads(message)
