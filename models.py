import json
import uuid

from mongokit import Document

from database import connection, db

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
        'field_count': int,
        'field_types': list,
        'collection': basestring,
    }

    def __init__(self, source, field_count, field_types, collection, label=None):
        self.source = source
        self.field_count = field_count
        self.field_types = field_types
        self.collection = collection
        self.label = label
        if self.label is None:
            self.label = self.source

    def __repr__(self):
        return u"<Meta {0}>".format(self.label)

    def to_dict(self):
        return {
            'source': self.source,
            'field_count': self.field_count,
            'field_types': self.field_types,
            'collection': self.collection,
            'label': self.label
        }

class DataSet(object):
    """The raw data stored in collections determined by meta data"""
    pass

class DataSetHandler(object):
    """Wrapper to data set information"""

    def __init__(self):
        self.data_set_meta = {}
        self.db = db

    def add(self, data):
        """When adding determine whether there is matching meta data by;
        - source
        - field count
        - field types

        If match is found then store in relevant collection, otherwise
        create new meta data record and collection
        """
        data = json.loads(data)
        meta_data = self.get_or_create_meta(data)
        self.db[meta_data.get('collection')].insert(self.get_raw_data(data))

    def get_raw_data(self, data):
        """Remove irrelevant fields and leave just the actual data"""
        raw_data = data.copy()
        irrelevant_fields = [
            "source"
        ]

        for irrelevant_field in irrelevant_fields:
            if raw_data.get(irrelevant_field):
                raw_data.pop(irrelevant_field)

        return raw_data

    def get_or_create_meta(self, data):
        """Check for matching meta data record otherwise create one"""
        source = self.get_source(data)
        field_count = self.get_field_count(data)
        field_types = self.get_field_types(data)

        meta_data_key = json.dumps((source, field_count, field_types))

        if meta_data_key not in self.data_set_meta:
            # get meta that matches source, field_count and field_types
            meta_data = self.db.data_set_meta.find_one({
                'source': source,
                'field_count': field_count,
                'field_types': field_types
            })
            # if not found generate uid for data set collection name
            # and store meta record and add to data set meta list
            if meta_data is None:
                meta_data_collection = u"{0}".format(uuid.uuid1())
                meta_data = DataSetMeta(
                    source=source,
                    field_count=field_count,
                    field_types=field_types,
                    collection=meta_data_collection
                ).to_dict()
                self.db.data_set_meta.insert(meta_data)
            self.data_set_meta[meta_data_key] = meta_data

        return self.data_set_meta[meta_data_key]

    def get_source(self, data):
        """Determine source of data"""
        return data.get('source')

    def get_field_count(self, data):
        """Determine the # of fields in data"""
        raw_data = self.get_raw_data(data)
        return len(raw_data)

    def get_field_types(self, data):
        """Determine the field types of raw data"""
        raw_data = self.get_raw_data(data)
        field_types = []
        for field in raw_data.values():
            field_types.append("{0}".format(type(field)))
        return field_types
