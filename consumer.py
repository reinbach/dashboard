import gevent
import zmq

from config import DASHBOARD_DATA_URI

def consumer_service(data_set_handler):
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
            data_set_handler.add(msg)
            #TODO message needs to be pushlished
            # to users that are connected
        gevent.sleep(0.1)

    socket.close()