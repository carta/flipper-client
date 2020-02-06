import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import Condition, MemoryFeatureFlagStore
from flipper.bucketing import Percentage, PercentageBucketer
from flipper.client import FeatureFlagClient
from flipper.contrib.storage import FeatureFlagStoreMeta
from flipper.exceptions import FlagDoesNotExistError
from flipper.flag import FeatureFlag


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.name = self.txt()
        self.store = MemoryFeatureFlagStore()
        self.client = FeatureFlagClient(self.store)
        self.flag = FeatureFlag(self.name, self.client)

    def txt(self):
        return uuid4().hex


class TestName(BaseTest):
    def test_name_gets_set(self):
        self.assertEqual(self.name, self.flag.name)


class TestIsEnabled(BaseTest):
    def test_returns_true_when_feature_enabled(self):
        self.store.create(self.name)

        self.flag.enable()

        self.assertTrue(self.flag.is_enabled())

    def test_returns_false_when_feature_disabled(self):
        self.store.create(self.name)

        self.flag.enable()
        self.flag.disable()

        self.assertFalse(self.flag.is_enabled())

    def test_returns_false_when_flag_does_not_exist(self):
        self.assertFalse(self.flag.is_enabled())

    def test_returns_true_if_condition_specifies(self):
        self.store.create(self.name, is_enabled=True)
        self.flag.add_condition(Condition(foo=True))

        self.assertTrue(self.flag.is_enabled(foo=True))

    def test_returns_false_if_condition_specifies(self):
        self.store.create(self.name, is_enabled=True)
        self.flag.add_condition(Condition(foo=True))

        self.assertFalse(self.flag.is_enabled(foo=False))

    def test_returns_false_if_feature_disabled_despite_condition(self):
        self.store.create(self.name, is_enabled=False)
        self.flag.add_condition(Condition(foo=True))

        self.assertFalse(self.flag.is_enabled(foo=True))

    def test_returns_false_if_bucketer_check_returns_false(self):
        bucketer = MagicMock()
        bucketer.check.return_value = False

        self.store.create(self.name, is_enabled=True)
        self.flag.set_bucketer(bucketer)

        self.assertFalse(self.flag.is_enabled())

    def test_returns_true_if_bucketer_check_returns_true(self):
        bucketer = MagicMock()
        bucketer.check.return_value = True

        self.store.create(self.name, is_enabled=True)
        self.flag.set_bucketer(bucketer)

        self.assertTrue(self.flag.is_enabled())

    def test_forwards_conditions_to_bucketer(self):
        bucketer = MagicMock()

        self.store.create(self.name, is_enabled=True)
        self.flag.set_bucketer(bucketer)

        self.flag.is_enabled(foo=True)

        bucketer.check.assert_called_with(foo=True)


class TestExists(BaseTest):
    def test_when_object_does_not_exist_returns_false(self):
        self.assertFalse(self.flag.exists())

    def test_when_object_does_exist_returns_true(self):
        self.store.create(self.name)

        self.assertTrue(self.flag.exists())


class TestDestroy(BaseTest):
    def test_object_remains_instance_of_flag_class(self):
        self.store.create(self.name)

        self.flag.destroy()

        self.assertTrue(isinstance(self.flag, FeatureFlag))

    def test_status_switches_to_disabled(self):
        self.store.create(self.name)

        self.flag.enable()
        self.flag.destroy()

        self.assertFalse(self.flag.is_enabled())

    def test_client_is_called_with_correct_args(self):
        client = MagicMock()
        flag = FeatureFlag(self.name, client)
        flag.destroy()

        client.destroy.assert_called_once_with(self.name)

    def test_raises_for_nonexistent_flag(self):
        with self.assertRaises(FlagDoesNotExistError):
            self.flag.destroy()


class TestEnable(BaseTest):
    def test_is_enabled_will_be_true(self):
        self.store.create(self.name)

        self.flag.enable()

        self.assertTrue(self.flag.is_enabled())

    def test_is_enabled_will_be_true_if_disable_was_called_earlier(self):
        self.store.create(self.name)

        self.flag.disable()
        self.flag.enable()

        self.assertTrue(self.flag.is_enabled())

    def test_client_is_called_with_correct_args(self):
        client = MagicMock()
        flag = FeatureFlag(self.name, client)
        flag.enable()

        client.enable.assert_called_once_with(self.name)

    def test_raises_for_nonexistent_flag(self):
        with self.assertRaises(FlagDoesNotExistError):
            self.flag.enable()


class TestDisable(BaseTest):
    def test_is_enabled_will_be_false(self):
        self.store.create(self.name, True)
        self.flag.disable()

        self.assertFalse(self.flag.is_enabled())

    def test_is_enabled_will_be_false_if_enable_was_called_earlier(self):
        self.store.create(self.name)
        self.flag.enable()
        self.flag.disable()

        self.assertFalse(self.flag.is_enabled())

    def test_client_is_called_with_correct_args(self):
        client = MagicMock()
        flag = FeatureFlag(self.name, client)
        flag.disable()

        client.disable.assert_called_once_with(self.name)

    def test_raises_for_nonexistent_flag(self):
        with self.assertRaises(FlagDoesNotExistError):
            self.flag.disable()


class TestSetClientData(BaseTest):
    def test_calls_backend_with_correct_feature_name(self):
        self.store.set_meta = MagicMock()

        client_data = {self.txt(): self.txt()}

        self.store.create(self.name)
        self.flag.set_client_data(client_data)

        [actual, _] = self.store.set_meta.call_args[0]

        self.assertEqual(self.name, actual)

    def test_calls_backend_with_instance_of_meta(self):
        self.store.set_meta = MagicMock()

        client_data = {self.txt(): self.txt()}

        self.store.create(self.name)
        self.flag.set_client_data(client_data)

        [_, meta] = self.store.set_meta.call_args[0]

        self.assertIsInstance(meta, FeatureFlagStoreMeta)

    def test_calls_backend_with_correct_meta_client_data(self):
        self.store.set_meta = MagicMock()

        client_data = {self.txt(): self.txt()}

        self.store.create(self.name)
        self.flag.set_client_data(client_data)

        [_, meta] = self.store.set_meta.call_args[0]

        self.assertEqual(client_data, meta.client_data)

    def test_calls_backend_with_non_null_meta_created_date(self):
        self.store.set_meta = MagicMock()

        client_data = {self.txt(): self.txt()}

        self.store.create(self.name)
        self.flag.set_client_data(client_data)

        [_, meta] = self.store.set_meta.call_args[0]

        self.assertIsNotNone(meta.created_date)

    def test_calls_backend_exactly_once(self):
        self.store.set_meta = MagicMock()

        client_data = {self.txt(): self.txt()}

        self.store.create(self.name)
        self.flag.set_client_data(client_data)

        self.assertEqual(1, self.store.set_meta.call_count)

    def test_merges_new_values_with_existing(self):
        existing_data = {"existing_key": self.txt()}

        self.store.create(self.name, client_data=existing_data)

        new_data = {"new_key": self.txt()}
        self.flag.set_client_data(new_data)

        item = self.store.get(self.name)

        self.assertEqual({**existing_data, **new_data}, item.meta["client_data"])

    def test_can_override_existing_values(self):
        existing_data = {"existing_key": self.txt()}

        self.store.create(self.name, client_data=existing_data)

        new_data = {"existing_key": self.txt(), "new_key": self.txt()}
        self.flag.set_client_data(new_data)

        item = self.store.get(self.name)

        self.assertEqual(new_data, item.meta["client_data"])

    def test_raises_for_nonexistent_flag(self):
        client_data = {self.txt(): self.txt()}

        with self.assertRaises(FlagDoesNotExistError):
            self.flag.set_client_data(client_data)


class TestGetClientData(BaseTest):
    def test_gets_expected_key_value_pairs(self):
        client_data = {self.txt(): self.txt()}

        self.store.create(self.name, client_data=client_data)

        result = self.flag.get_client_data()

        self.assertEqual(client_data, result)

    def test_raises_for_nonexistent_flag(self):
        with self.assertRaises(FlagDoesNotExistError):
            self.flag.get_client_data()


class TestGetMeta(BaseTest):
    def test_includes_created_date(self):
        client_data = {self.txt(): self.txt()}

        self.store.create(self.name, client_data=client_data)

        meta = self.flag.get_meta()

        self.assertTrue("created_date" in meta)

    def test_includes_client_data(self):
        client_data = {self.txt(): self.txt()}

        self.store.create(self.name, client_data=client_data)

        meta = self.flag.get_meta()

        self.assertEqual(client_data, meta["client_data"])

    def test_raises_for_nonexistent_flag(self):
        with self.assertRaises(FlagDoesNotExistError):
            self.flag.get_meta()


class TestAddCondition(BaseTest):
    def test_condition_gets_included_in_meta(self):
        condition_checks = {self.txt(): True}
        condition = Condition(**condition_checks)

        self.store.create(self.name)
        self.flag.add_condition(condition)

        meta = self.flag.get_meta()

        self.assertTrue(condition.to_dict() in meta["conditions"])

    def test_condition_gets_appended_to_meta(self):
        condition_checks = {self.txt(): True}
        condition = Condition(**condition_checks)

        self.store.create(self.name)
        self.flag.add_condition(condition)
        self.flag.add_condition(condition)

        meta = self.flag.get_meta()

        self.assertEqual(2, len(meta["conditions"]))


class TestSetBucketer(BaseTest):
    def test_bucketer_gets_included_in_meta(self):
        percentage_value = 0.1
        bucketer = PercentageBucketer(percentage=Percentage(percentage_value))

        self.store.create(self.name)
        self.flag.set_bucketer(bucketer)

        meta = self.flag.get_meta()

        self.assertEqual(bucketer.to_dict(), meta["bucketer"])


class TestSetConditions(BaseTest):
    def test_overrides_previous_conditions(self):
        self.store.create(self.name)
        overriden_condition = Condition(value=True)
        new_conditions = [Condition(new_value=True), Condition(id__in=[1, 2])]

        self.flag.add_condition(overriden_condition)
        self.flag.set_conditions(new_conditions)

        conditions_array = self.flag.get_meta()["conditions"]
        expected_conditions_array = [
            {"new_value": [{"variable": "new_value", "value": True, "operator": None}]},
            {"id": [{"variable": "id", "value": [1, 2], "operator": "in"}]},
        ]

        self.assertEqual(expected_conditions_array, conditions_array)
