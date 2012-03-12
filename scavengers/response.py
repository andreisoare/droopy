# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: andrei@thesunnytrail.com (Andrei Soare)
#
# Interface for the Response object from social networks.

class Response(dict):
  def __init__(self, status, raw_data='', email=''):
    self['status'] = status
    self['raw_data'] = raw_data
    self['email'] = email

  def is_error(self):
    return True if self['status'] > 400 else False
