from datetime import datetime
import json
import unittest
from uuid import uuid4

from flipper.contrib.storage import FeatureFlagStoreMeta


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.now = int(datetime.now().timestamp())

    def txt(self):
        return uuid4().hex


class TestToJSON(BaseTest):
    def test_includes_correct_created_date(self):
        meta = FeatureFlagStoreMeta(self.now, {})
        self.assertEqual(self.now, meta.toJSON()['created_date'])

    def test_includes_correct_client_data(self):
        client_data = {
            'foo': 99,
            'bar': 'ajds'
        }
        meta = FeatureFlagStoreMeta(self.now, client_data)
        self.assertEqual(client_data, meta.toJSON()['client_data'])
