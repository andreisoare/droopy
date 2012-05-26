# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from Foursquare.

import simplejson
import httplib
import datetime

from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request, NOT_FOUND_ERROR_CODE

FOURSQUARE = "foursquare"
FOURSQUARE_HOST = "api.foursquare.com"
FOURSQUARE_PATH = "/v2/users/search"
OAUTH = '1BRZVFUP3JAHHMYCTYPTQGX31UM3AHASNEHGHCTLBRDJAN2Y'

class FoursquareScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(FoursquareScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    response = self._foursquare(email)
    return simplejson.dumps({
                              'type' : FOURSQUARE,
                              'response' : response
                            })

  def _foursquare(self, email):
    today = datetime.date.today()
    v = "%d%d%d" % (today.year, today.month, today.day)
    params = {
              'email': email,
              'oauth_token': OAUTH,
              'v': v,
             }
    response = http_request(email, "GET", FOURSQUARE_HOST, FOURSQUARE_PATH,
                                                    params, httplib.HTTPS_PORT)

    if response.is_error() or len(response['raw_data']) == 0:
      response['status'] = NOT_FOUND_ERROR_CODE
      return response
    data = simplejson.loads(response['raw_data'])['response']['results']
    if len(data) is 0:
      response['status'] = NOT_FOUND_ERROR_CODE
      return response

    return FoursquareResponse(response)

class FoursquareResponse(Response):
  def __init__(self, response):
    super(FoursquareResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    data = simplejson.loads(self['raw_data'])
    info = data['response']['results'][0]

    self['display_name'] = "%s %s" % (info['firstName'], info['lastName'])
    self['gender'] = info['gender']
    self['location'] = info['homeCity']
    self['profiles'] = ['foursquare.com/user/' + info['id']]
    #TODO(diana) check contact field
    if 'bio' in info:
      self['profiles'].append(info['bio'])

