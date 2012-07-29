TESTING = False

DATABASE = {
    'MONGO_DB_NAME': "dashboard",
    'MONGO_DB_HOST': "localhost",
    'MONGO_DB_PORT': 27017,
    'MONGO_DB_TEST': "dashboard_test",
}

DASHBOARD_DATA_URI = "tcp://127.0.0.1:5000"
DASHBOARD_IO_URI = "tcp://127.0.0.1:5001"