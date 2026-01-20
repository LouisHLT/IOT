from collections import deque

from config import MAX_POINTS

def make_station_buffers():
    """ 
        Create buffers for storing station data.

        Returns:
            A dictionary containing deques for each sensor value.
    """
    return {
        "timestamps": deque(maxlen=MAX_POINTS),
        "temp": deque(maxlen=MAX_POINTS),
        "hum": deque(maxlen=MAX_POINTS),
        "co2": deque(maxlen=MAX_POINTS),
        "o2": deque(maxlen=MAX_POINTS),
        "light": deque(maxlen=MAX_POINTS),
        "last_seen": None,
    }