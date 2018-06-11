import json


class Job():

    def __init__(self, data, options):
        self.data = data
        self.options = options

    def get_json(self):
        json_data = {
            "data": self.data,
            "options": self.options,
            "status": "created"
        }
        return json.dumps(json_data)
