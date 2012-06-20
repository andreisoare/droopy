# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from Github.

import simplejson
import httplib
import logging

import global_settings
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request, format_url

GITHUB = "github"
GITHUB_HOST = "api.github.com"
GITHUB_PATH = "/legacy/user/email/"

class GithubScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(GithubScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    logging.info('%s got email %s' % (GITHUB, email))
    response = self._github(email)
    logging.info('%s finished with email %s with status %s' %
          (GITHUB, email, response['status']))
    return simplejson.dumps({
                              'type' : GITHUB,
                              'response' : response
                            })

  def _github(self, email):
    response = http_request(email, "GET", GITHUB_HOST,
               "%s%s" % (GITHUB_PATH, email), {}, httplib.HTTPS_PORT)

    if response.is_error():
      return response

    return GithubResponse(response)

class GithubResponse(Response):
  def __init__(self, response):
    super(GithubResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    info = simplejson.loads(response['raw_data'])['user']

    if 'name' in info and info['name']:
      self['display_name'] = info['name']
    if 'location' in info and info['location']:
      self['location'] = info['location']
    if 'login' in info and info['login']:
      self['username'] = info['login']
      self['profiles'] = ["github.com/" + info['login']]
    if 'blog' in info and info['blog']:
      self['profiles'].append(format_url(info['blog']))

