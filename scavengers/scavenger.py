# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: andrei@thesunnytrail.com (Andrei Soare)
#
# Scevenger interface: gathers any type of personal data around an email address
# from different services.
#
# The Scavenger receives an email on the in_tube, processes it and then puts the
# result on the out_tube, together with the number of calls it made to the utilized
# service.

import global_settings
import logging

from beanstalk_worker import Worker
from base.beanstalk_utils import connect_beanstalk

class Scavenger(Worker):
  def __init__(self, proc_id, in_tube, out_tube, api_key=None):
    """Initializes class attributes.
       proc_id  = unique string identification for worker
       in_tube  = input data tube
       out_tube = output data tube
       api_key  = optional api key for some scavengers
    """
    host, port = global_settings.BEANSTALKD.split(':')
    super(Scavenger, self).__init__(in_tube, host, int(port))

    self.api_key = api_key
    self.in_tube = in_tube
    self.out_tube = out_tube
    self.out_queue = connect_beanstalk(host, port, out_tube, out_tube)

    logging.info("Scavenger %s started!" % proc_id)

  def on_job(self, job):
    """Process one job from beanstalk queue."""
    job.bury()
#    logging.info("JOB %s" % job.body)
    result = self.process_job(job)
    self.enqueue_result(result)
    job.done()

  def process_job(self, job):
    """This needs to be overwritten by subclasses"""
    return None

  def enqueue_result(self, result):
    self.out_queue.put(result)

