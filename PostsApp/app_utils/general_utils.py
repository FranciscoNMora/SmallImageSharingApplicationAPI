from datetime import datetime
import time
from functools import wraps

import pytz
from django.conf import settings


def unix_timestamp(dt: datetime) -> int:
    """Turn datetime into Unix timestamp integer"""
    try:
        dt = pytz.utc.localize(dt)
    except ValueError:
        pass
    local = pytz.timezone(settings.TIME_ZONE)
    return int(time.mktime(dt.astimezone(local).timetuple()))


def disable_for_loaddata(signal_handler):
    """Disable signals while loading data in tests"""
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs['raw']:
            return
        signal_handler(*args, **kwargs)
    return wrapper