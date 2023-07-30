from datetime import datetime

class Sub():
    def __init__(self, client: int, end_time: datetime = datetime.now(), sub_in_days = 0):
        self.client = client
        self.end_time = end_time
        self.max_sub = 3
        self.min_sub = 0
        self.sub_in_days = sub_in_days

        if self.sub_in_days == 0:
            self.sub_in_days = (self.end_time - datetime.now()).days
        if self.sub_in_days < 0:
            self.sub_in_days = 0
    def convert_sub(self, client, new_client, new_days):
        ...
        