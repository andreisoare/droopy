# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from Foursquare.

import simplejson
import httplib
import datetime
import logging

import global_settings
from scavenger import Scavenger
from scavenger_config import FOURSQUARE_OAUTH
from response import Response
from scavenger_utils import http_request, NOT_FOUND_ERROR_CODE, process_profiles

FOURSQUARE = "foursquare"
FOURSQUARE_HOST = "api.foursquare.com"
FOURSQUARE_PATH = "/v2/users/search"

class FoursquareScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(FoursquareScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    logging.info('%s got email %s' % (FOURSQUARE, email))
    response = self._foursquare(email)
    logging.info('%s finished with email %s with status %s' %
          (FOURSQUARE, email, response['status']))
    return simplejson.dumps({
                              'type' : FOURSQUARE,
                              'response' : response
                            })

  def _foursquare(self, email):
    today = datetime.date.today()
    v = "%d%d%d" % (today.year, today.month, today.day)
    params = {
              'email': email,
              'oauth_token': FOURSQUARE_OAUTH,
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
    profiles = []

    firstName = ''
    lastName = ''
    if 'firstName' in info and info['firstName']:
      firstName = info['firstName']
    if 'lastName' in info and info['lastName']:
      lastName = info['lastName']
    if firstName or lastName:
      self['display_name'] = ('%s %s' % (firstName, lastName)).strip()

    if 'gender' in info and info['gender']:
      self['gender'] = info['gender']
    if 'homeCity' in info and info['homeCity']:
      self['location'] = info['homeCity']
    if 'id' in info and info['id']:
      profiles = ['foursquare.com/user/' + info['id']]

    #TODO(diana) check if contact field has others than fb, twitter
    if 'contact' in info:
      if 'facebook' in info['contact'] and info['contact']['facebook']:
        profiles.append(
              "facebook.com/profile.php?id=%s" % info['contact']['facebook'])
      if 'twitter' in info['contact'] and info['contact']['twitter']:
        profiles.append("twitter.com/%s" % info['contact']['twitter'])

    if 'bio' in info and info['bio']:
      profiles.append(info['bio'])

    if profiles:
      response = process_profiles(profiles)
      self['profiles'] = profiles
      if response:
        self.enhance_response(response)

