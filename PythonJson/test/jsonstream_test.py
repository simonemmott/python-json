'''
Created on 18 Dec 2018

@author: simon
'''
import unittest, json, os
from jsonstream import *
from utilities.writers import StringWriter
from utilities.readers import StringReader


class TestJsonWriter(unittest.TestCase):


    def test_new_writer(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        assert jw is not None
        
    def test_write_name(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.name('test_name')
        
        assert sw.__str__() == '"test_name": '
        
    def test_write_name_value(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.name('test_string')
        jw.value('a string')
        
        assert sw.__str__() == '"test_string": "a string"'
        
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.name('test_num')
        jw.value(123)
        
        assert sw.__str__() == '"test_num": 123'
        
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.name('test_float')
        jw.value(1.234)
        
        assert sw.__str__() == '"test_float": 1.234'
        
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.name('test_bool')
        jw.value(True)
        
        assert sw.__str__() == '"test_bool": true'
        
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.name('test_null')
        jw.value(None)
        
        assert sw.__str__() == '"test_null": null'
        
        
    def test_write_empty_object(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_object()
        jw.end_object()
        
        assert sw.__str__() == '{}'
        
    def test_write_object_with_value(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_object()
        jw.name('a_num')
        jw.value(123)
        jw.end_object()
        
        assert sw.__str__() == '{"a_num": 123}'
        
    def test_write_object_with_two_values(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_object()
        jw.name('a_num')
        jw.value(123)
        jw.name('a_str')
        jw.value('aaaa')
        jw.end_object()
        
        assert sw.__str__() == '{"a_num": 123, "a_str": "aaaa"}'
        
    def test_write_object_with_three_values(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_object()
        jw.name('a_num')
        jw.value(123)
        jw.name('a_str')
        jw.value('aaaa')
        jw.name('a_bool')
        jw.value(False)
        jw.end_object()
        
        assert sw.__str__() == '{"a_num": 123, "a_str": "aaaa", "a_bool": false}'
        
    def test_write_empty_list(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_list()
        jw.end_list()
        
        assert sw.__str__() == '[]'
        
    def test_write_list_with_value(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_list()
        jw.value(123)
        jw.end_list()
        
        assert sw.__str__() == '[123]'
        
    def test_write_list_with_two_values(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_list()
        jw.value(123)
        jw.value(456)
        jw.end_list()
        
        assert sw.__str__() == '[123, 456]'
        
    def test_write_list_with_three_values(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_list()
        jw.value(123)
        jw.value(456)
        jw.value(789)
        jw.end_list()
        
        assert sw.__str__() == '[123, 456, 789]'
        
    def test_write_name_and_object(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.name('test_obj')
        jw.begin_object()
        jw.name('a_num')
        jw.value(123)
        jw.end_object()
        
        assert sw.__str__() == '"test_obj": {"a_num": 123}'
        
    def test_write_name_and_list(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.name('test_obj')
        jw.begin_list()
        jw.value(123)
        jw.value(456)
        jw.end_list()
        
        assert sw.__str__() == '"test_obj": [123, 456]'
        
    def test_write_object_and_object(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_object()
        jw.name('obj')
        jw.begin_object()
        jw.name('a_num')
        jw.value(456)
        jw.end_object()
        jw.end_object()
        
        assert sw.__str__() == '{"obj": {"a_num": 456}}'
        
    def test_write_object_and_list(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_object()
        jw.name('lst')
        jw.begin_list()
        jw.value(123)
        jw.value(456)
        jw.end_list()
        jw.end_object()
        
        assert sw.__str__() == '{"lst": [123, 456]}'
        
    def test_write_list_of_objects(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_list()
        
        jw.begin_object()
        jw.name('a_num')
        jw.value(123)
        jw.end_object()

        jw.begin_object()
        jw.name('a_num')
        jw.value(456)
        jw.end_object()

        jw.end_list()
        
        assert sw.__str__() == '[{"a_num": 123}, {"a_num": 456}]'
        
    def test_write_list_of_lists(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_list()
        
        jw.begin_list()
        jw.value(123)
        jw.value(456)
        jw.end_list()

        jw.begin_list()
        jw.value('a')
        jw.value('b')
        jw.end_list()

        jw.end_list()
        
        assert sw.__str__() == '[[123, 456], ["a", "b"]]'
        
    def test_write_object_of_lists(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_object()
        
        jw.name('lst1')
        jw.begin_list()
        jw.value(123)
        jw.value(456)
        jw.end_list()

        jw.name('lst2')
        jw.begin_list()
        jw.value('a')
        jw.value('b')
        jw.end_list()

        jw.end_object()
        
        assert sw.__str__() == '{"lst1": [123, 456], "lst2": ["a", "b"]}'
        
    def test_write_object_of_objects(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_object()
        
        jw.name('lst')
        jw.begin_list()
        jw.value(123)
        jw.value(456)
        jw.end_list()

        jw.name('obj')
        jw.begin_object()
        jw.name('a_num')
        jw.value(123)
        jw.name('a_str')
        jw.value('abc')
        jw.name('a_lst')
        jw.begin_list()
        jw.value('a')
        jw.value('b')
        jw.end_list()
        jw.end_object()
        
        jw.name('a_val')
        jw.value(789)

        jw.end_object()
        
        assert sw.__str__() == '{"lst": [123, 456], "obj": {"a_num": 123, "a_str": "abc", "a_lst": ["a", "b"]}, "a_val": 789}'
        
    def test_pretty_write_object_with_two_values(self):
        sw = StringWriter()
        jw = JsonWriter(sw, indent='  ')
        
        jw.begin_object()
        jw.name('a_num')
        jw.value(123)
        jw.name('a_str')
        jw.value('aaaa')
        jw.end_object()
        
        expected =  '{'+os.linesep+'  "a_num": 123, '+os.linesep+'  "a_str": "aaaa"'+os.linesep+'}'
        assert sw.__str__() == expected
        
    def test_pretty_write_object_of_objects(self):
        sw = StringWriter()
        jw = JsonWriter(sw, indent='  ')
        
        jw.begin_object()
        
        jw.name('lst')
        jw.begin_list()
        jw.value(123)
        jw.value(456)
        jw.end_list()

        jw.name('obj')
        jw.begin_object()
        jw.name('a_num')
        jw.value(123)
        jw.name('a_str')
        jw.value('abc')
        jw.name('a_lst')
        jw.begin_list()
        jw.value('a')
        jw.value('b')
        jw.end_list()
        jw.end_object()
        
        jw.name('a_val')
        jw.value(789)

        jw.end_object()
        
        ew = StringWriter()
        ew.writeln('{')
        ew.writeln('  "lst": [')
        ew.writeln('    123, ')
        ew.writeln('    456')
        ew.writeln('  ], ')
        ew.writeln('  "obj": {')
        ew.writeln('    "a_num": 123, ')
        ew.writeln('    "a_str": "abc", ')
        ew.writeln('    "a_lst": [')
        ew.writeln('      "a", ')
        ew.writeln('      "b"')
        ew.writeln('    ]')
        ew.writeln('  }, ')
        ew.writeln('  "a_val": 789')
        ew.write('}')
        assert sw.__str__() == ew.__str__()
        
    def test_marshall_object_of_objects(self):
        sw = StringWriter()
        jw = JsonWriter(sw)
        
        jw.begin_object()
        
        jw.name('lst')
        jw.begin_list()
        jw.value(123)
        jw.value(456)
        jw.end_list()

        jw.name('obj')
        jw.begin_object()
        jw.name('a_num')
        jw.value(123)
        jw.name('a_str')
        jw.value('abc')
        jw.name('a_lst')
        jw.begin_list()
        jw.value('a')
        jw.value('b')
        jw.end_list()
        jw.end_object()
        
        jw.name('a_val')
        jw.value(789)

        jw.end_object()
        
        d = json.loads(sw.__str__())
        
        assert d['lst'][0] == 123
        assert d['lst'][1] == 456
        assert d['obj']['a_num'] == 123
        assert d['obj']['a_str'] == 'abc'
        assert d['obj']['a_lst'][0] == 'a'
        assert d['obj']['a_lst'][1] == 'b'
        assert d['a_val'] == 789        
        
    def test_marshall_pretty_object_of_objects(self):
        sw = StringWriter()
        jw = JsonWriter(sw, indent='  ')
        
        jw.begin_object()
        
        jw.name('lst')
        jw.begin_list()
        jw.value(123)
        jw.value(456)
        jw.end_list()

        jw.name('obj')
        jw.begin_object()
        jw.name('a_num')
        jw.value(123)
        jw.name('a_str')
        jw.value('abc')
        jw.name('a_lst')
        jw.begin_list()
        jw.value('a')
        jw.value('b')
        jw.end_list()
        jw.end_object()
        
        jw.name('a_val')
        jw.value(789)

        jw.end_object()
        
        d = json.loads(sw.__str__())
        
        assert d['lst'][0] == 123
        assert d['lst'][1] == 456
        assert d['obj']['a_num'] == 123
        assert d['obj']['a_str'] == 'abc'
        assert d['obj']['a_lst'][0] == 'a'
        assert d['obj']['a_lst'][1] == 'b'
        assert d['a_val'] == 789        
        
        
SIMPLE_JSON = '{"a_num": 123, "a_str": "abc", "a_bool": true, "a_float": 1.23}'

class TestJsonReader(unittest.TestCase):
        
    def test_new_instance(self):
         
        sr = StringReader(SIMPLE_JSON)
        jr = JsonReader(sr)
        assert jr is not None
        
    def test_has_next(self):

        sr = StringReader(SIMPLE_JSON)
        jr = JsonReader(sr)
        
        assert jr.next != None
        assert jr.has_next()
        
    def test_peek(self):

        sr = StringReader(SIMPLE_JSON)
        jr = JsonReader(sr)
        
        node = jr.peek()
        
        assert isinstance(node, JsonStartObjectNode)
        
    def test_type_is(self):

        sr = StringReader(SIMPLE_JSON)
        jr = JsonReader(sr)
        
        node = jr.peek()
        
        assert node.type_is(JsonNodeType.START_OBJECT)
        
    def test_begin_object(self):
        sr = StringReader(SIMPLE_JSON)
        jr = JsonReader(sr)
        
        node = jr.peek()
        
        assert jr.begin_object() == node
        
    
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()