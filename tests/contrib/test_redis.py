import unittest
from uuid import uuid4

import fakeredis

from ff_client import RedisFeatureFlagStore


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.redis = fakeredis.FakeStrictRedis()
        self.store = RedisFeatureFlagStore(self.redis)

    def txt(self):
        return uuid4().hex


class TestCreate(BaseTest):
    def test_value_is_true_when_created_with_default_true(self):
        feature_name = self.txt()

        self.store.create(feature_name, default=True)

        self.assertTrue(self.store.get(feature_name))

    def test_value_is_true_when_created_with_default_false(self):
        feature_name = self.txt()

        self.store.create(feature_name, default=False)

        self.assertFalse(self.store.get(feature_name))

    def test_value_is_false_when_created_with_default(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.assertFalse(self.store.get(feature_name))

    def test_sets_correct_value_in_redis_with_default_true(self):
        feature_name = self.txt()

        self.store.create(feature_name, default=True)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertEqual(b'1', self.redis.get(key))

    def test_sets_correct_value_in_redis_with_default_false(self):
        feature_name = self.txt()

        self.store.create(feature_name, default=False)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertEqual(b'0', self.redis.get(key))

    def test_sets_correct_value_in_redis_with_default(self):
        feature_name = self.txt()

        self.store.create(feature_name, default=False)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertEqual(b'0', self.redis.get(key))


class TestGet(BaseTest):
    pass


class TestSet(BaseTest):
    def test_sets_correct_value_when_true(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, True)

        self.assertTrue(self.store.get(feature_name))

    def test_sets_correct_value_when_false(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, False)

        self.assertFalse(self.store.get(feature_name))

    def test_sets_correct_value_in_redis_when_true(self):
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.set(feature_name, True)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertEqual(b'1', self.redis.get(key))

    def test_sets_correct_value_in_redis_when_false(self):
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.set(feature_name, False)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertEqual(b'0', self.redis.get(key))

    def test_sets_correct_value_when_not_created(self):
        feature_name = self.txt()

        self.store.set(feature_name, True)

        self.assertTrue(self.store.get(feature_name))


class TestDelete(BaseTest):
    def test_returns_false_after_delete(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, True)
        self.store.delete(feature_name)

        self.assertFalse(self.store.get(feature_name))

    def test_does_not_raise_when_deleting_key_that_does_not_exist(self):
        feature_name = self.txt()

        self.store.delete(feature_name)

        self.assertFalse(self.store.get(feature_name))

    def test_deletes_value_from_redis(self):
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.delete(feature_name)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertIsNone(self.redis.get(key))
