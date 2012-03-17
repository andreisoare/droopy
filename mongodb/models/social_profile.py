# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: andrei@thesunnytrail.com (Andrei Soare)
#
# Client data model.

import logging

from base_document import BaseDocument
from datetime import datetime

class FlickrResponse:


class Client(BaseDocument):
  structure = {
    # Last modified time
    'time' : datetime,

    # Email address
    'email' : unicode,

    # Personal data
    'age': [int, int],
    'name': unicode,
    'location': unicode,

    # Data from Flickr
    'flickr_status': int,
    'flickr_link': unicode,
    'flickr_parsed': dict,

    # Data from Github
    'github_status': int.
    'github_raw': unicode,
    'github_link': unicode,

    # And so on ...
  }

  required_fields = ['email', 'time']

  default_values = {
    'flickr_status': 0,
    'github_status': 0,
  }

  indexes = [
    {'fields': ['email'], 'unique': True},
  ]
