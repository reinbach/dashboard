import json
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

        for meta_data in self.request.get_data_set_meta().values():
            # get initial data for meta data type
            response = meta_data.to_json_friendly()
            response['data'] = meta_data.get_data()
            self.emit("meta_data_types", json.dumps(response))

        while True:
            action = dict(poller.poll(1))

            if action:
                # record the data and send to client
                data = sock.recv()
                self.emit("new_data", data)
            gevent.sleep(0.1)

        sock.close()

    def on_stream(self, msg):
        self.spawn(self.subscribe)