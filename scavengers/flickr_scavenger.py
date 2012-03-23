# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)

import simplejson
from scavenger import Scavenger
from scavenger_utils import http_request, NOT_FOUND_ERROR_CODE
from response import Response

FLICKR = 'flickr'
FLICKR_HOST = "api.flickr.com"
FLICKR_PATH = "/services/rest/"
FLICKR_KEY = 'd75138bb5caa8f70bb5b3dc071e19e6e'
FLICKR_PWD = '1e7edafa40c76873'
RESPONSE_PREFIX_LENGTH = 14

class FlickrScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(FlickrScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    response = self._flickr(email)
    return simplejson.dumps(
                            { 'type' : FLICKR,
                              'response' : response
                            }
                           )

  def _flickr(self, email):
    queries = {"email": "flickr.people.findByEmail",
               "user": "flickr.people.getInfo"
               }

    params =  {"method": queries['email'],
               "api_key": FLICKR_KEY,
               "find_email": email,
               "format": "json"
               }

    response = http_request(email, "GET", FLICKR_HOST, FLICKR_PATH, params)
    if response.is_error():
     return response

    message = response['raw_data']
    # Jump over the first 14 characters and get the actual JSON
    message = message[RESPONSE_PREFIX_LENGTH:len(message)-1]
    data = simplejson.loads(message)

    if data['stat'] == 'fail':
      response['status'] = NOT_FOUND_ERROR_CODE
      return response

    user_id = data['user']['id']

    params['method'] = queries['user']
    params['user_id'] = str(user_id)
    del params['find_email']

    response = http_request(email, "GET", FLICKR_HOST, FLICKR_PATH, params)
    if response.is_error():
      return response

    return FlickrResponse(response)

class FlickrResponse(Response):
  def __init__(self, response):
    super(FlickrResponse, self).__init__(response['status'],
                         response['raw_data'], response['email'])

    message = response['raw_data']
    message = message[RESPONSE_PREFIX_LENGTH:len(message)-1]
    data = simplejson.loads(message)

    self['username'] = data['person']['username']['_content']
    self['display_name'] = data['person']['realname']['_content']
    self['location'] = data['person']['location']['_content']
    self['profiles'] = [data['person']['profileurl']['_content']]

