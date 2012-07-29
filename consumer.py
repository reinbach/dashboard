import gevent
import json
import zmq

from config import DASHBOARD_DATA_URI, DASHBOARD_IO_URI


def consumer_service(data_set_handler):
    """Accept the data from various clients"""
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(DASHBOARD_DATA_URI)

    stream_to_io = context.socket(zmq.PUB)
    stream_to_io.bind(DASHBOARD_IO_URI)

    print "Start consumer service...."

    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    while True:
        data = dict(poller.poll(1))

        if data.get(socket) == zmq.POLLIN:
            msg = socket.recv()
            data = data_set_handler.add(msg)
            stream_to_io.send(json.dumps(data))
        gevent.sleep(0.1)

    socket.close()
    stream_to_io.close()