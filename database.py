from mongokit import Connection

import config

connection = Connection(
    config.DATABASE['MONGO_DB_HOST'],
    config.DATABASE['MONGO_DB_PORT']
)

class DBLayer(object):

    def __init__(self):
        self.db = None

    def get_db(self):
        if self.db is None:
            db_name = config.DATABASE['MONGO_DB_NAME']
            if config.TESTING:
                db_name = config.DATABASE['MONGO_DB_TEST']
            self.db = connection[db_name]
        return self.db

    def drop_database(self):
        """Drop database, only if in testing mode"""
        if config.TESTING:
            connection.drop_database(config.DATABASE['MONGO_DB_TEST'])
