# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)

from scavenger import Scavenger
from scavenger_utils import http_request

MYSPACE_HOST = "api.myspace.com"
MYSPACE_PATH = "/opensearch/people/"

class MySpaceScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(MySpaceScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
  # TODO(diana) how to get email?
    email = ??
    response = self._myspace(email)
  # TODO(diana) how we send the response

  def _myspace(self, email):
    params = {
                'searchTerms' : email,
                'searchBy' : 'email',
                'format' : 'json'
             }
    response = http_request(email, "GET", MYSPACE_HOST, MYSPACE_PATH, params)

    if response.is_error():
      return response

    return MySpaceResponse(response)

class MySpaceResponse(Response):
  def __init__(self, response):
    super(MySpaceResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
# TODO(diana) parse raw_data
    self['display_name'] =
    self['gender'] =
    self['age'] =
    self['location'] =

