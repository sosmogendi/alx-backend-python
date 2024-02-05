#!/usr/bin/env python3
""" Module for testing utils """

from parameterized import parameterized
import unittest
from unittest.mock import patch
from utils import (access_nested_map, get_json, memoize)
import requests


class TestAccessNestedMap(unittest.TestCase):
    """ Test class for the access_nested_map function """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {'b': 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self, input_map, path, expected_output):
        """ Test that access_nested_map returns the expected result """
        self.assertEqual(access_nested_map(input_map, path), expected_output)

    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b')
    ])
    def test_access_nested_map_exception(self, input_map, path, expected_exception):
        """ Test that a KeyError is raised for the specified inputs """
        with self.assertRaises(KeyError) as exception_context:
            access_nested_map(input_map, path)
        self.assertEqual(f"KeyError('{expected_exception}')", repr(exception_context.exception))


class TestGetJson(unittest.TestCase):
    """ Test class for the get_json function """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    def test_get_json(self, url, expected_payload):
        """ Test that get_json returns the expected JSON payload """
        config = {'return_value.json.return_value': expected_payload}
        patcher = patch('requests.get', **config)
        mock_get = patcher.start()
        self.assertEqual(get_json(url), expected_payload)
        mock_get.assert_called_once()
        patcher.stop()


class TestMemoize(unittest.TestCase):
    """ Test class for the memoize decorator """

    def test_memoize(self):
        """ Test that calling a_property twice returns the correct result
        and a_method is only called once using assert_called_once
        """

        class TestClass:
            """ Test Class for wrapping with memoize """

            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, 'a_method') as mock_method:
            test_instance = TestClass()
            test_instance.a_property()
            test_instance.a_property()
            mock_method.assert_called_once()
