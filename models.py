import datetime
import json
import pymongo
import uuid

from mongokit import Document

import config

from database import connection, DBLayer

@connection.register
class DataSetMeta(Document):
    """Meta data for the data set

    Meta data is made up of;
    - source: data set source (eg: IP address)
    - label
    - field count: total # of fields in the data set
    - field types: data type of each field
    - field headers: if no headers provided then use first record data
    - collection: where data set is stored
    """
    __collection__ = 'data_set_meta'
    use_dot_notation = True

    structure = {
        'source': unicode,
        'label': unicode,
        'field_types': list,
        'collection_id': basestring,
    }

    def __init__(self, source=None, field_types=None):
        super(DataSetMeta, self).__init__()
        self.source = source
        self.field_types = field_types
        self._id = None
        self.collection_id = None
        self.label = None

        self.dblayer = DBLayer()

    def __repr__(self):
        return u"<Meta {0}>".format(self.get_label())

    def set_values(self, data):
        if data is None:
            return
        self.set_id(data)
        self.set_label(data)
        self.set_collection_id(data)

    def set_id(self, data):
        if data.get('_id', False):
            self._id = u"{0}".format(data.get('_id'))
        else:
            self._id = None

    def get_id(self):
        return self._id

    def set_label(self, data):
        self.label = data.get('label', None)
        if self.label is None:
            self.label = self.get_source()

    def set_collection_id(self, data):
        self.collection_id = data.get('collection_id', None)

    def get_collection_id(self):
        return u"{0}".format(self.collection_id)

    def get_source(self):
        return self.source

    def get_field_types(self):
        return self.field_types

    def get_label(self):
        if self.label is None:
            return self.get_source()
        return self.label

    def get(self):
        """Pull data from database"""
        db = self.dblayer.get_db()
        data = db.data_set_meta.find_one({
            'source': self.get_source(),
            'field_types': self.get_field_types()
        })
        self.set_values(data)

    def to_json_friendly(self):
        data = {
            'source': self.get_source(),
            'field_types': self.get_field_types(),
            'collection_id': self.get_collection_id(),
            'label': self.get_label()
        }
        if self.get_id() is not None:
            data['_id'] = self.get_id()
        return data

    def get_meta_data_key(self):
        return json.dumps((
            self.source,
            self.field_types
        ))

    def get_data(self, limit=config.RESULT_SET_LIMIT):
        """Get data and split into separate streams based on the number of fields

        Example:
        Data received [10, 34], [13, 53] ...

        Return:
        data[1] = [10, 14]
        data[2] = [34, 53]
        """
        db = self.dblayer.get_db()
        result = db[self.get_collection_id()].find(
            sort=[("_id", pymongo.DESCENDING)],
            limit=limit
        )
        data = []
        for x in result:
            current_data = x.get("data")
            if not data:
                data = [[] for field in range(len(current_data))]
            for i in range(len(current_data)):
                data[i].append(current_data[i])
        return data

    def save(self):
        """Save data to database

        If no collection value need to create one
        """
        if self.collection_id is None:
            self.collection_id = u"{0}".format(uuid.uuid1())
        db = self.dblayer.get_db()
        db.data_set_meta.save(self.to_json_friendly())
        self.get()

    def save_data(self, data):
        """Dave data, make sure we have a timestamp

        If no timestamp, then add
        """
        db = self.dblayer.get_db()
        if not data.get("timestamp", False):
            data.update(
                timestamp=datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%s")
            )
        db[self.get_collection_id()].insert(data)
        return DataSet(data).to_json_friendly()


class DataSet(object):
    """The raw data stored in collections determined by meta data"""
    def __init__(self, data):
        self.data = data

    def to_json_friendly(self):
        data = {
            'data': self.data.get('data')
        }
        if self.data.get('_id') is not None:
            data['_id'] = u"{0}".format(self.data.get("_id"))
        return data

class DataSetHandler(object):
    """Wrapper to data set information"""

    def __init__(self):
        self.data_set_meta = {}
        self.dblayer = DBLayer()

    def get_data_set_meta(self):
        db = self.dblayer.get_db()
        for meta in db.data_set_meta.find():
            meta_data = DataSetMeta(
                meta.get("source"),
                meta.get("field_types")
            )
            meta_data.set_values(meta)
            self.data_set_meta[meta_data.get_meta_data_key()] = meta_data
        return self.data_set_meta

    def add(self, data):
        """When adding determine whether there is matching meta data by;
        - source
        - field count
        - field types

        If match is found then store in relevant collection, otherwise
        create new meta data record and collection
        """
        complete_data = json.loads(data)

        source = self.get_source(complete_data)
        field_types = self.get_field_types(complete_data)
        meta_data = self.get_or_create_meta(source, field_types)

        new_data = meta_data.save_data(self.get_raw_data(complete_data))

        return new_data

    def get_or_create_meta(self, source, field_types):
        """Check for matching meta data record otherwise create one"""
        meta_data = DataSetMeta(source, field_types)
        meta_data.get()

        if meta_data.get_meta_data_key() not in self.data_set_meta.keys():
            if meta_data.get_id() is None:
                meta_data.save()
            self.data_set_meta[meta_data.get_meta_data_key()] = meta_data

        return meta_data

    def get_source(self, data):
        """Determine source of data"""
        return data.get('source')

    def get_field_types(self, data):
        """Determine the field types of raw data"""
        raw_data = self.get_raw_data(data)
        if raw_data.get("data", False):
            values_list = raw_data.get("data")
        else:
            values_list = raw_data.values()
        field_types = []
        for field in values_list:
            field_types.append("{0}".format(type(field)))
        return field_types

    def get_raw_data(self, data):
        """Remove irrelevant fields and leave just the actual data"""
        raw_data = data.copy()
        irrelevant_fields = [
            "source",
        ]

        for irrelevant_field in irrelevant_fields:
            if raw_data.get(irrelevant_field):
                raw_data.pop(irrelevant_field)

        return raw_data

