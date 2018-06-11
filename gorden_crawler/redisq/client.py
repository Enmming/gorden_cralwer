# -*- coding: utf-8 -*-
import redis


class RedisqClient():

    def __init__(self, queue_name, host="localhost", port=6379, password=None, db=0):
        self.r = redis.StrictRedis(host=host, password=password, port=port, db=db)
        self.queue_name = "redisq:%s:queue" % queue_name

    def pushTask(self, task):
        return self.r.lpush(self.queue_name, task.get_json())