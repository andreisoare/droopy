# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: diana.tiriplica@gmail.com (Diana-Victoria Tiriplica)
#
# Facebook identity model.

import logging

from base_document import BaseDocument
from datetime import datetime


class FacebookIdentity(BaseDocument):

  structure = {
    # Last modified time
    'time': datetime,

    # Facebook id
    'profile_id' : int,

    # Facebook username
    'profile_user' : unicode,

    # Facebook response
    'response' : dict,
  }

  required_fields = ['time', 'profile_id', 'profile_user']

  indexes = [
    {'fields': ['profile_id'], 'unique': True},
  ]

