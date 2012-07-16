from mongokit import Connection

from config import DATABASE

connection = Connection(
    DATABASE['MONGO_DB_HOST'],
    DATABASE['MONGO_DB_PORT']
)

db = connection[DATABASE['MONGO_DB_NAME']]