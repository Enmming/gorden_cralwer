# -*- coding: utf-8 -*-
import redis

class BeeQueueClient():

    def __init__(self, queue_name_prefix, host="localhost", port=6379, password=None, db=0):
        self.r = redis.StrictRedis(host=host, password=password, port=port, db=db)
        self.queue_name_prefix = queue_name_prefix

    def pushJob(self, job):
        job_id = self.r.incr(self.queue_name_prefix + "id")
        self.r.hset(self.queue_name_prefix + "jobs", job_id, job.get_json())
        self.r.lpush(self.queue_name_prefix + "waiting", job_id)
        
        return job_id
