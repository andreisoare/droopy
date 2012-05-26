# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: andrei@thesunnytrail.com (Andrei Soare)
#
# SocialProfile data model.

import logging

from base_document import BaseDocument
from datetime import datetime


class SocialProfile(BaseDocument):

  structure = {
    # Last modified time
    'time': datetime,

    # Email address
    'email': unicode,

    # Networks with usernames
    'network_candidates' : dict,

    # Personal data
    'age': [int, int],
    'location': unicode,
    'username': unicode,
    'display_name': unicode,
    'profiles': [unicode],
    'gender': unicode,

    # Data from Flickr
    'flickr_status': int,
    'flickr_link': unicode,
    'flickr_parsed': dict,

    # Data from Github
    'github_status': int,
    'github_link': unicode,
    'github_parsed': dict,

    # Data from GooglePlus
    'google_plus_status': int,
    'google_plus_link': unicode,
    'google_plus_parsed': dict,

    # Data from Jigsaw
    'jigsaw_status': int,
    'jigsaw_link': unicode,
    'jigsaw_parsed': dict,

    # Data from Myspace
    'myspace_status': int,
    'myspace_link': unicode,
    'myspace_parsed': dict,

    # Data from Yahoo
    'yahoo_status': int,
    'yahoo_link': unicode,
    'yahoo_parsed': dict,

    # Data from Foursquare
    'foursquare_status': int,
    'foursquare_link': unicode,
    'foursquare_parsed': dict,
  }

  required_fields = ['email', 'time']

  default_values = {
    'flickr_status': 0,
    'github_status': 0,
    'google_plus_status': 0,
    'jigsaw_status': 0,
    'myspace_status': 0,
    'yahoo_status': 0,
    'foursquare_status': 0,
    'age': [],
    'profiles': [],
    'network_candidates': {},
  }

  indexes = [
    {'fields': ['email'], 'unique': True},
  ]
