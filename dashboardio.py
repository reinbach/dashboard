import gevent
import zmq

from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin

from config import DASHBOARD_IO_URI

class DashboardIOApp(BaseNamespace, BroadcastMixin):

    def subscribe(self):
        """Send list of Meta Data Types and then
        stream data and new Meta Data Types onwards to connected clients
        """
        context = zmq.Context()
        sock = context.socket(zmq.SUB)
        sock.setsockopt(zmq.SUBSCRIBE, "")
        sock.connect(DASHBOARD_IO_URI)

        poller = zmq.Poller()
        poller.register(sock, zmq.POLLIN)

        self.emit("meta_data_types", self.request.get_data_set_meta())

        while True:
            action = dict(poller.Poll(1))

            if action:
                # record the data and send to client
                # if new meta data set created, need
                # to send that on to client as well
                #
                #TODO need to indicate the meta type for
                # the data being streamed
                data = sock.recv()
                self.emit("new_data", data)
            gevent.sleep(0.1)

        sock.close()

    def on_stream(self, msg):
        self.spawn(self.subscribe)