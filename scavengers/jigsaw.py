# Copyright 2012 Droopy @Sunnytrail Insight Labs Inc. All rights reserved
# Author: tabara.mihai@gmail.com (Mihai Tabara)

# Jigsaw scavenger: gathers any type of personal data around an email address
# from Jigsaw network

# The scanvanger receives a job consisting an email address and returns a result
# of a JSON format. (None if user not found) within 1 API call
# Example of fields returned:
# https://www.jigsaw.com/rest/searchContact.json?token=rgr5hkhww2dfgcgarrj66baa
# &email=asadat@salesforce.com

import simplejson as json
from scavenger_utils import http_request
from urllib import urlopen

JIGSAW_HOST = "www.jigsaw.com"
JIGSAW_PATH = "/rest/searchContact.json"

JIGSAW_KEY = 'rgr5hkhww2dfgcgarrj66baa'

def jigsaw(email):
  params = {
              "token" : JIGSAW_KEY,
              "email" : email,
           }

  response = http_request("GET", JIGSAW_HOST, JIGSAW_PATH, params, 443)
  message = response.read()
  data = json.loads(message)

  if data['totalHits'] == 0:
    return None

  return data
