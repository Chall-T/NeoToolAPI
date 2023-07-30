from datetime import datetime
import time


def get_datetime():
    date = datetime.now()
    return date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def get_timestamp():
    return str(int(time.time()))

def get_timezone():
    return str(datetime.now().astimezone(None).strftime("GMT%z"))