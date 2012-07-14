import gevent
import zmq

from config import DASHBOARD_DATA_URI

def consumer_service():
    """Accept the data from various clients"""
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(DASHBOARD_DATA_URI)

    print "Start consumer service...."

    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    while True:
        data = dict(poller.poll(1))

        if data.get(socket) == zmq.POLLIN:
            msg = socket.recv()
            #TODO message needs to be handled
        gevent.sleep(0.1)

    socket.close()