# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: andrei@thesunnytrail.com (Andrei Soare)
#
# Base Document class

from mongokit import Document

class BaseDocument(Document):
  use_dot_notation = True
