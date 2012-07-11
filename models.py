class DataSetMeta(object):
    """Meta data for the data set

    Meta data is made up of;
    - source: data set source (eg: IP address)
    - label
    - field count: total # of fields in the data set
    - field types: data type of each field
    - field headers: if no headers provided then use first record data
    - collection: where data set is stored
    """
    pass

class DataSet(object):
    """The raw data stored in collections determined by meta data"""
    pass


class DataSetHandler(object):
    """Wrapper to data set information"""

    def __init__(self):
        self.data_set_meta = []
        self.data_set = []

    def add(self, data):
        """When adding determine whether there is matching meta data by;
        - source
        - field count
        - field types

        If match is found then store in relevant collection, otherwise
        create new meta data record and collection
        """
        meta_data = self.get_or_create_meta(data)
        #TODO add data set record with meta data

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

        meta_data_key = (source, field_count, field_types)

        if meta_data_key in self.data_set_meta:
            #TODO need to determine good id for meta data
            # that is used for data sets
            pass

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