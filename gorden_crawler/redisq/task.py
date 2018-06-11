# -*- coding: utf-8 -*-
import time
import json


class Task():

    def __init__(self, data, task_time=None):
        if not isinstance(data, str):
            raise TypeError("Data must be a JSON string ")

        self.data = data

        if not task_time:
            self.time = int(time.time())
        else:
            self.time = task_time

    def get_json(self):
        return json.dumps([0, self.time, "{{placeholder}}", 0]).replace("\"{{placeholder}}\"", self.data)