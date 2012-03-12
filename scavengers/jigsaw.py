# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved
# Author: tabara.mihai@gmail.com (Mihai Tabara)

# Jigsaw scavenger: gathers any type of personal data around an email address
# from Jigsaw network

# The scanvanger receives a job consisting an email address and returns a result
# of a JSON format. (None if user not found) within 1 API call
# Example of fields returned:
# https://www.jigsaw.com/rest/searchContact.json?token=rgr5hkhww2dfgcgarrj66baa
# &email=asadat@salesforce.com

import json
from scavenger_utils import http_request

JIGSAW_HOST = "www.jigsaw.com"
JIGSAW_PATH = "/rest/searchContact.json"

JIGSAW_KEY = 'rgr5hkhww2dfgcgarrj66baa'
HTTPS_PORT = 443

def jigsaw(email):
  params = {
              "token" : JIGSAW_KEY,
              "email" : email,
           }

  response = http_request(email, "GET", JIGSAW_HOST, JIGSAW_PATH, params, HTTPS_PORT)

  if response.is_error():
    return response
  message = response['raw_data']
  data = json.loads(message)

  if data['totalHits'] == 0:
    return None

  return data
