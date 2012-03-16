# Copyright 2011 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: andrei@thesunnytrail.com (Andrei Soare)
#
# Benstalkd Worker class: an easy way to develop scripts for handling jobs put
# on a beanstalkd work queue server.
#
# Basic Usage:
#
#     from beanstalk_worker import Worker
#
#     class MyWorker(Worker):
#         def on_job(self, job):
#             pass
#
#     MyWorker(host='...', port='...', tube='...').run()

from base.beanstalk_utils import connect_beanstalk
import logging
import threading
import time

from beanstalkc import SocketError

class Job(object):
    """ Wrapper around a job object. Adds done() method as synonym to delete() """
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, name):
        return getattr(self.obj, name)

    def done(self):
        return self.obj.delete()


class Worker(object):
    log = logging.getLogger()

    def __init__(self, tube='default', host='localhost', port=11300):
        self.tube = tube
        self.host, self.port = host, port
        self.conn = connect_beanstalk(host, port, tube, tube)

    def run(self):
        """ Worker main loop. Reserve job and execute. """
        try:
            while True:
                self.cycle()
        except KeyboardInterrupt:
            self.log.info('got exit request. bye bye!')
            pass

    def cycle(self):
        job = None
        try:
            self.log.info('waiting for jobs.')

            job = self.conn.reserve()

            if job is not None:
                self.log.info('got job with id #%d' % job.jid)
                self.on_job(Job(job))

        except SocketError:
            # TODO: this does not work when restarting beanstalk
            self.conn = connect_beanstalk(self.host, self.port, self.tube, self.tube)

        except Exception, e:
            self.log.exception('got unexpected exception when running job')
            if job is not None: job.bury()

    def on_job(self, job):
        """ Handles a new job

        When a new job arrives this method is called. You should override
        this method in the class implementing the worker.
        """
        pass

    def _reschedule_job(self, job, delay):
      logging.info('Postpone job %s with delay %d' % (job, delay))
      self.conn.put(job, delay=delay)

class AsyncWorker(Worker, threading.Thread):

    def __init__(self, *args, **kwargs):
        Worker.__init__(self, *args, **kwargs)
        threading.Thread.__init__(self)
