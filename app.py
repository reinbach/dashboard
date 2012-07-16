import gevent
import os

from flask import Flask, render_template
from gevent import monkey
from socketio.server import SocketIOServer
from werkzeug.wsgi import SharedDataMiddleware

from consumer import consumer_service
from models import DataSetHandler

monkey.patch_all()

app = Flask(__name__)
app.debug = True

data_set_handler = DataSetHandler()

@app.route("/")
def home():
    return render_template("index.html")

def main():
    http_app = SharedDataMiddleware(app, {
        '/': os.path.join(os.path.dirname(__file__), 'static')
    })
    socket_server = SocketIOServer(
        ('', 8000), http_app,
        namespace='socket.io',
        policy_server=False
    )

    gevent.joinall([
        gevent.spawn(socket_server.serve_forever),
        gevent.spawn(consumer_service, data_set_handler)
    ])

if __name__ == "__main__":
    main()