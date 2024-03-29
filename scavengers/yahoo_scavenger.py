# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)

import yql
import simplejson
import logging

import global_settings
from response import Response
from scavenger import Scavenger
from scavenger_config import YAHOO_KEY, YAHOO_PWD
from scavenger_utils import NOT_FOUND_ERROR_CODE, OK_CODE, process_profiles

YAHOO = "yahoo"

class YahooScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(YahooScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    logging.info('%s got email %s' % (YAHOO, email))
    response = self._yahoo(email)
    logging.info('%s finished with email %s with status %s' %
          (YAHOO, email, response['status']))
    return simplejson.dumps({
                              'type' : YAHOO,
                              'response' : response
                            })

  def _yahoo(self, email):
    username = email[0:email.find('@')]
    host = email[email.find('@')+1:]

    domains = ['yahoo', 'ymail', 'rocketmail']
    for domain in domains:
      to_check = True if host.find(domain) >= 0 else False
      if to_check is True:
        break

    if to_check is False:
      return Response(NOT_FOUND_ERROR_CODE,
        'Email address not matching yahoo standard\'s naming policies', email)

    y = yql.TwoLegged(YAHOO_KEY, YAHOO_PWD)
    yql_object = y.execute("select * from social.profile where guid in \
                          (select guid from yahoo.identity \
                          where yid='%s')" % username)

    if yql_object.count == None:
      return Response(NOT_FOUND_ERROR_CODE, '', email)

    return YahooResponse(Response(OK_CODE, yql_object.one(), email))

class YahooResponse(Response):
  def __init__(self, response):
    super(YahooResponse, self).__init__(response['status'],
                                        response['raw_data'],
                                        response['email'])
    data = response['raw_data']
    profiles = []

    # TODO(mihai): Add a proper method to validate yahoo addresses
    self['username'] = response['email'][0:response['email'].find('@')]
    if 'location' in data and data['location']:
      self['location'] = data['location']
    if 'gender' in data and data['gender']:
      self['gender'] = data['gender']
    if 'displayAge' in data and data['displayAge']:
      self['age'] = data['displayAge']
    if 'profileUrl' in data and data['profileUrl']:
      profiles = [data['profileUrl']]

    display_name = None
    if 'nickname' in data and data['nickname']:
      display_name = data['nickname']
    if 'familyName' in data and 'givenName' in data:
      display_name = ' '.join([data['familyName'], data['givenName']])
    if display_name:
      self['display_name'] = display_name

    if profiles:
      response = process_profiles(profiles)
      self['profiles'] = profiles
      if response:
        self.enhance_response(response)

