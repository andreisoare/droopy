# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from MySpace.

import simplejson
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request

MYSPACE_HOST = "api.myspace.com"
MYSPACE_PATH = "/opensearch/people/"

class MySpaceScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(MySpaceScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    response = self._myspace(email)
    return simplejson.dumps(response)

  def _myspace(self, email):
    params = {'searchTerms': email,
              'searchBy': 'email',
              'format': 'json'
              }
    response = http_request(email, "GET", MYSPACE_HOST, MYSPACE_PATH, params)

    if response.is_error():
      return response

    return MySpaceResponse(response)

class MySpaceResponse(Response):
  def __init__(self, response):
    super(MySpaceResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
# TODO(diana) check if profiles are given back
    data = simplejson.loads(self['raw_data'])
    info = data['entry'][0]

    self['display_name'] = info['displayName']
    self['gender'] = info['gender']
    self['age'] = info['age']
    self['location'] = info['location']
    self['profiles'] = [info['profileUrl']]

