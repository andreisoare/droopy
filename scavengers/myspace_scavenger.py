# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from MySpace.

import simplejson
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request, format_url

MYSPACE = "myspace"
MYSPACE_HOST = "api.myspace.com"
MYSPACE_PATH = "/opensearch/people/"

class MyspaceScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(MyspaceScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    response = self._myspace(email)
    return simplejson.dumps({
                              'type' : MYSPACE,
                              'response' : response
                            })

  def _myspace(self, email):
    params = {'searchTerms': email,
              'searchBy': 'email',
              'format': 'json'
              }
    response = http_request(email, "GET", MYSPACE_HOST, MYSPACE_PATH, params)

    if response.is_error():
      return response

    return MyspaceResponse(response)

class MyspaceResponse(Response):
  def __init__(self, response):
    super(MyspaceResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
# TODO(diana) check if profiles are given back
    data = simplejson.loads(self['raw_data'])
    info = data['entry'][0]

    self['display_name'] = info['displayName']
    self['gender'] = info['gender']
    self['age'] = info['age']
    self['location'] = info['location']
    self['profiles'] = [format_url(info['profileUrl'])]

