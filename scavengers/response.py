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
    return True if self['status'] >= 400 else False

  def enhance_response(self, fb_response):
    # TODO(diana) check if other fields are public
    if not 'display_name' in self:
      first_name = ''
      last_name = ''
      if 'first_name' in fb_response and fb_response['first_name']:
        first_name = fb_response['first_name']
      if 'last_name' in fb_response and fb_response['last_name']:
        last_name = fb_response['last_name']
      if first_name or last_name:
        self['display_name'] = ('%s %s' % (first_name, last_name)).strip()
    if not 'gender' in self and 'gender' in fb_response and\
                                                          fb_response['gender']:
      self['gender'] = fb_response['gender']
    if not 'username' in self and 'username' in fb_response and\
                                                        fb_response['username']:
      self['username'] = fb_response['username']

