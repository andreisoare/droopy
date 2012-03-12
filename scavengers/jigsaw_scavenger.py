# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: tabara.mihai@gmail.com (Mihai Tabara)

import simplejson
from scavenger_utils import http_request, NOT_FOUND_ERROR_MESSAGE

JIGSAW_HOST = "www.jigsaw.com"
JIGSAW_PATH = "/rest/searchContact.json"
JIGSAW_KEY = 'rgr5hkhww2dfgcgarrj66baa'
HTTPS_PORT = 443

class JigsawScavenger(Scavenger):
  def __init__(self, proc_id, in_tube, out_tube):
    super(JigsawScavenger, self).__init__(proc_id, in_tube, out_tube)

  def process_job(self, job):
    email = job.body
    response = self.flickr(email)
    return simplejson.dumps(response)

  def _jigsaw(self, email):
    params = {
                "token" : JIGSAW_KEY,
                "email" : email,
             }

    response = http_request(email, "GET", JIGSAW_HOST, JIGSAW_PATH,
                            params, HTTPS_PORT)
    if response.is_error():
      return response

    message = response['raw_data']
    data = simplejson.loads(message)

    if data['totalHits'] == 0:
      response['status'] = NOT_FOUND_ERROR_MESSAGE
      return response

    return JigsawResponse(response)

class JigsawResponse(Response):
  def __init__(self, response):
    super(JigsawResponse, self).__init__(response['status'],
                         response['raw_data'], response['email'])

    message = response['raw_data']
    data = simplejson.loads(message)

    self['display_name'] = data['contacts'][0]['firstname'] + ' ' + \
                            data['contacts'][0]['lastname']
    self['location'] = data['contacts'][0]['city'] + ' ' + \
                        data['contacts'][0]['state']

