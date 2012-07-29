import json
import unittest

import config
# need to set the testing flag here
# so it sets the database flag correctly
config.TESTING = True

import models
import database

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.handler = models.DataSetHandler()

    def tearDown(self):
        database.DBLayer().drop_database()


class TestDataSetMeta(BaseTest):

    def test_meta(self):
        """Test creating a data set meta object"""
        data = {'source': 'data', 'field_types': ['int']}
        meta = models.DataSetMeta(data.get('source') , data.get('field_types'))
        assert meta.source == 'data'
        assert meta.field_types == data.get('field_types')
        assert meta.get_meta_data_key() == json.dumps(data.values())

    def test_meta_save(self):
        """Test saving meta data"""
        data = {'source': 'data', 'field_types': ['int']}
        meta = models.DataSetMeta(data.get('source') , data.get('field_types'))
        meta.save()
        assert meta.get_id() is not None
        assert meta.get_collection_id() is not None

    def test_meta_save_data(self):
        """Test saving data on meta"""
        meta_data = {'source': 'data', 'field_types': ['int']}
        meta = models.DataSetMeta(
            meta_data.get('soure'),
            meta_data.get('field_types')
        )
        meta.save()
        data = {"data": [0.78, 0.07, 0.3, 0.92]}
        saved_data = meta.save_data(data)
        assert data.get("data") == saved_data.get("data")
        assert u"{0}".format(data.get("_id")) == saved_data.get("_id")
        all_saved_data = meta.get_data()
        assert [data.get('data')[0]] in all_saved_data


class TestDataSetHandler(BaseTest):

    def test_data_set_meta(self):
        """Test that data set meta list is empty"""
        assert self.handler.data_set_meta == {}

    def test_get_source(self):
        """Test getting source value from data"""
        data = {"source": "data", "data": [0.78, 0.07, 0.3, 0.92]}
        source = self.handler.get_source(data)
        assert data.get('source') == source

    def test_get_raw_data(self):
        """Test getting raw data from data"""
        data = {"source": "data", "data": [0.78, 0.07, 0.3, 0.92]}
        raw_data = self.handler.get_raw_data(data)
        data.pop("source")
        assert raw_data == data

    def test_get_field_types(self):
        """Test getting field types from data"""
        data = {"source": "data", "data": [0.78, 0.07, 0.3, 0.92]}
        expected_field_types = [
            "<type 'float'>",
            "<type 'float'>",
            "<type 'float'>",
            "<type 'float'>"
        ]
        field_types = self.handler.get_field_types(data)
        assert expected_field_types == field_types

    def test_get_or_create_meta(self):
        """Test getting meta data"""
        data = {"source": "data", "data": [0.78, 0.07, 0.3, 0.92]}
        source = self.handler.get_source(data)
        field_types = self.handler.get_field_types(data)
        meta = self.handler.get_or_create_meta(source, field_types)
        expected_meta = models.DataSetMeta(source, field_types)
        expected_meta.get()
        assert meta.get_id() == expected_meta.get_id()
        assert meta in self.handler.data_set_meta.values()

        meta2 = self.handler.get_or_create_meta(source, field_types)
        assert meta.get_collection_id() == meta2.get_collection_id()

    def test_get_data_set_meta(self):
        """Test getting data set meta objects"""
        data1 = {"source": "data", "data": [0.78, 0.07, 0.3, 0.92]}
        meta1 = self.handler.get_or_create_meta(
            self.handler.get_source(data1),
            self.handler.get_field_types(data1)
        )
        data2 = {"source": "message", "data": ["hello", "world"]}
        meta2 = self.handler.get_or_create_meta(
            self.handler.get_source(data2),
            self.handler.get_field_types(data2)
        )
        meta_list = self.handler.get_data_set_meta()
        #test
        print "meta list: ", meta_list
        assert meta1 in meta_list.values()
        assert meta1.get_meta_data_key() in meta_list.keys()
        assert meta_list[meta1.get_meta_data_key()] == meta1
        assert meta2 in meta_list.values()
        assert meta2.get_meta_data_key() in meta_list.keys()
        assert meta_list[meta2.get_meta_data_key()] == meta2

    def test_adding_data(self):
        """Test saving data"""
        data = {"source": "data", "data": [0.78, 0.07, 0.3, 0.92]}
        data_saved = self.handler.add(json.dumps(data))
        data_saved.pop("_id")
        assert self.handler.get_raw_data(data) == data_saved

    def test_get_data(self):
        """Test getting data"""
        data1 = {"source": "data", "data": [0.78, 0.07, 0.3]}
        data2 = {"source": "data", "data": [0.65, 0.34, 0.54]}
        self.handler.add(json.dumps(data1))
        self.handler.add(json.dumps(data2))
        field_types = self.handler.get_field_types(data1)
        meta = self.handler.get_or_create_meta(
            self.handler.get_source(data1),
            field_types
        )
        data_saved = meta.get_data()
        assert len(field_types) == len(data_saved)
        assert 2 == len(data_saved[0])

if __name__ == "__main__":
    unittest.main()