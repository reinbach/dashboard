import datetime
import gevent
import json
import random
import zmq

from gevent import monkey

from config import DASHBOARD_DATA_URI

monkey.patch_all()

def random_float():
    """Generate random float value"""
    return random.randint(1, 100) / 100.0

def random_int():
    """Generate random int value"""
    return random.randint(1, 100)

def random_time_delay(microseconds=True):
    """Generate random time delay"""
    delay = random.randint(1, 10)
    if microseconds:
        delay = delay / 100.0
    return delay

def random_message():
    """Generate random message"""
    data = [
        ("success", "Sale of Widget"),
        ("error", "504 Request"),
        ("warning", "Slow reponse"),
    ]
    return random.sample(data, 1)[0]

def random_data(data_size=4):
    """Generate random data"""
    data = []
    for x in xrange(0, data_size):
        data.append(random_float())
    return data

def data_producer():
    """Randomly produce data"""
    context = zmq.Context()
    data_socket = context.socket(zmq.PUSH)
    data_socket.connect(DASHBOARD_DATA_URI)

    while True:
        data_msg = json.dumps({
            'source': 'data',
            'data': random_data(),
            'timestamp': get_timestamp()
        })
        print "sending: ", data_msg
        data_socket.send(data_msg)
        gevent.sleep(random_time_delay())

    data_socket.close()

def get_timestamp():
    """Return a timestamp yyyy/mm/dd h:m:s"""
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def message_producer():
    """Randomly produce messages"""
    context = zmq.Context()
    message_socket = context.socket(zmq.PUSH)
    message_socket.connect(DASHBOARD_DATA_URI)

    while True:
        msg = json.dumps({
            'source': 'message',
            'data': random_message(),
            'timestamp': get_timestamp()
        })
        print "sending: ", msg
        message_socket.send(msg)
        gevent.sleep(random_time_delay(False))

    message_socket.close()

if __name__ == "__main__":
    gevent.joinall([
        gevent.spawn(data_producer),
        gevent.spawn(message_producer),
    ])
