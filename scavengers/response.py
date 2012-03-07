# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: andrei@thesunnytrail.com (Andrei Soare)
#
# Interface for the Response object from social networks.

class Respose(dict):
  def __init__(self, email):
    self['raw_data'] = ''
    self['status'] = 0
    self['email'] = email
