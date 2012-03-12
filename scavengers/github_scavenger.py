# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# This scavenger gets information about a user from Github.
#
# WARN (diana) This API is deprecated. Migrate to v3 when it will support
# search by email.

import simplejson
from scavenger import Scavenger
from response import Response
from scavenger_utils import http_request

GITHUB_HOST = "github.com"
GITHUB_PATH = "/api/v2/xml/user/email/"

class GitHubScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(GithubScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    response = self._github(email)
    return simplejson.dumps(response)

  def _github(self, email):
    response = http_request(email, "GET", GITHUB_HOST,
               "%s%s" % (GITHUB_PATH, email), {})

    if response.is_error():
      return response

    return GithubResponse(response)

class GithubResponse(Response):
  def __init__(self, response):
    super(MySpaceResponse, self).__init__(response['status'],
                          response['raw_data'], response['email'])
    info = ??
    self['display_name'] =
    self['location'] =
    self['profiles'] =
    self['username'] =
