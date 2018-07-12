import unittest
from uuid import uuid4

import fakeredis

from flipper import RedisFeatureFlagStore
from flipper.contrib.interface import FlagDoesNotExistError
from flipper.contrib.storage import FeatureFlagStoreItem


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.redis = fakeredis.FakeStrictRedis()
        self.store = RedisFeatureFlagStore(self.redis)

    def txt(self):
        return uuid4().hex


class TestCreate(BaseTest):
    def test_is_enabled_is_true_when_created_with_is_enabled_true(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        self.assertTrue(self.store.get(feature_name).is_enabled())

    def test_is_enabled_is_true_when_created_with_default_false(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=False)

        self.assertFalse(self.store.get(feature_name).is_enabled())

    def test_is_enabled_is_false_when_created_with_default(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.assertFalse(self.store.get(feature_name).is_enabled())

    def test_sets_correct_value_in_redis_with_is_enabled_true(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertTrue(
            FeatureFlagStoreItem.deserialize(self.redis.get(key)).is_enabled()
        )

    def test_sets_correct_value_in_redis_with_is_enabled_false(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=False)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertFalse(
            FeatureFlagStoreItem.deserialize(self.redis.get(key)).is_enabled()
        )

    def test_sets_correct_value_in_redis_with_default(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertFalse(
            FeatureFlagStoreItem.deserialize(self.redis.get(key)).is_enabled()
        )


class TestGet(BaseTest):
    pass


class TestSet(BaseTest):
    def test_sets_correct_value_when_true(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, True)

        self.assertTrue(self.store.get(feature_name).is_enabled())

    def test_sets_correct_value_when_false(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, False)

        self.assertFalse(self.store.get(feature_name).is_enabled())

    def test_sets_correct_value_in_redis_when_true(self):
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.set(feature_name, True)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertTrue(
            FeatureFlagStoreItem.deserialize(self.redis.get(key)).is_enabled()
        )

    def test_sets_correct_value_in_redis_when_false(self):
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.set(feature_name, False)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertFalse(
            FeatureFlagStoreItem.deserialize(self.redis.get(key)).is_enabled()
        )

    def test_sets_correct_value_when_not_created(self):
        feature_name = self.txt()

        self.store.set(feature_name, True)

        self.assertTrue(self.store.get(feature_name).is_enabled())


class TestDelete(BaseTest):
    def test_returns_false_after_delete(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, True)
        self.store.delete(feature_name)

        self.assertIsNone(self.store.get(feature_name))

    def test_does_not_raise_when_deleting_key_that_does_not_exist(self):
        feature_name = self.txt()

        self.store.delete(feature_name)

        self.assertIsNone(self.store.get(feature_name))

    def test_deletes_value_from_redis(self):
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.delete(feature_name)

        key = '/'.join([self.store.base_key, feature_name])

        self.assertIsNone(self.redis.get(key))


class TestSetClientData(BaseTest):
    def test_sets_values_correctly(self):
        feature_name = self.txt()
        self.store.create(feature_name)

        client_data = { self.txt(): self.txt() }
        self.store.set_client_data(feature_name, client_data)

        item = self.store.get(feature_name)

        self.assertEqual(client_data, item.meta['client_data'])

    def test_merges_new_values_with_existing(self):
        feature_name = self.txt()
        existing_data = { 'existing_key': self.txt() }

        self.store.create(feature_name, client_data=existing_data)

        new_data = { 'new_key': self.txt() }
        self.store.set_client_data(feature_name, new_data)

        item = self.store.get(feature_name)

        self.assertEqual({
            **existing_data,
            **new_data,
        }, item.meta['client_data'])

    def test_can_override_existing_values(self):
        feature_name = self.txt()
        existing_data = { 'existing_key': self.txt() }

        self.store.create(feature_name, client_data=existing_data)

        new_data = {
            'existing_key': self.txt(),
            'new_key': self.txt(),
        }
        self.store.set_client_data(feature_name, new_data)

        item = self.store.get(feature_name)

        self.assertEqual(new_data, item.meta['client_data'])

    def test_raises_exception_for_nonexistent_flag(self):
        feature_name = self.txt()
        with self.assertRaises(FlagDoesNotExistError):
            self.store.set_client_data(feature_name, { 'a': self.txt() })
