import unittest
from typing import Iterable, List, Tuple
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import Condition, FeatureFlagClient, MemoryFeatureFlagStore
from flipper.bucketing import Percentage, PercentageBucketer
from flipper.contrib.storage import FeatureFlagStoreMeta
from flipper.events import EventType, FlipperEventEmitter, FlipperEventSubscriber
from flipper.exceptions import FlagDoesNotExistError
from flipper.flag import FeatureFlag


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.store = MemoryFeatureFlagStore()
        self.client = FeatureFlagClient(self.store)

    def txt(self):
        return uuid4().hex


class TestIsEnabled(BaseTest):
    def test_returns_true_when_feature_enabled(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.enable(feature_name)

        self.assertTrue(self.client.is_enabled(feature_name))

    def test_returns_false_when_feature_disabled(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.disable(feature_name)

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_returns_false_when_feature_does_not_exist(self):
        feature_name = self.txt()

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_returns_true_if_condition_specifies(self):
        feature_name = self.txt()

        self.client.create(feature_name, is_enabled=True)
        self.client.add_condition(feature_name, Condition(foo=True))

        self.assertTrue(self.client.is_enabled(feature_name, foo=True))

    def test_returns_false_if_condition_specifies(self):
        feature_name = self.txt()

        self.client.create(feature_name, is_enabled=True)
        self.client.add_condition(feature_name, Condition(foo=True))

        self.assertFalse(self.client.is_enabled(feature_name, foo=False))

    def test_returns_false_if_feature_disabled_despite_condition(self):
        feature_name = self.txt()

        self.client.create(feature_name, is_enabled=False)
        self.client.add_condition(feature_name, Condition(foo=True))

        self.assertFalse(self.client.is_enabled(feature_name, foo=True))

    def test_returns_false_if_bucketer_check_returns_false(self):
        feature_name = self.txt()

        bucketer = MagicMock()
        bucketer.check.return_value = False

        self.client.create(feature_name, is_enabled=True)
        self.client.set_bucketer(feature_name, bucketer)

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_returns_true_if_bucketer_check_returns_true(self):
        feature_name = self.txt()

        bucketer = MagicMock()
        bucketer.check.return_value = True

        self.client.create(feature_name, is_enabled=True)
        self.client.set_bucketer(feature_name, bucketer)

        self.assertTrue(self.client.is_enabled(feature_name))

    def test_forwards_conditions_to_bucketer(self):
        feature_name = self.txt()

        bucketer = MagicMock()

        self.client.create(feature_name, is_enabled=True)
        self.client.set_bucketer(feature_name, bucketer)

        self.client.is_enabled(feature_name, foo=True)

        bucketer.check.assert_called_with(foo=True)


class TestCreate(BaseTest):
    def test_creates_and_returns_instance_of_feature_flag_class(self):
        feature_name = self.txt()

        flag = self.client.create(feature_name)

        self.assertTrue(isinstance(flag, FeatureFlag))

    def test_creates_flag_with_correct_name(self):
        feature_name = self.txt()

        flag = self.client.create(feature_name)

        self.assertEqual(feature_name, flag.name)

    def test_is_enabled_defaults_to_false(self):
        feature_name = self.txt()

        self.client.create(feature_name)

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_flag_can_be_enabled_on_create(self):
        feature_name = self.txt()

        self.client.create(feature_name, is_enabled=True)

        self.assertTrue(self.client.is_enabled(feature_name))

    def test_emits_pre_create_event_with_correct_args(self):
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.PRE_CREATE, f=listener)

        feature_name = self.txt()
        client_data = {"x": 10}

        self.client.events = events
        self.client.create(feature_name, is_enabled=True, client_data=client_data)

        listener.assert_called_with(
            feature_name, is_enabled=True, client_data=client_data
        )

    def test_emits_post_create_event_with_correct_args(self):
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.POST_CREATE, f=listener)

        feature_name = self.txt()
        client_data = {"x": 10}

        self.client.events = events
        self.client.create(feature_name, is_enabled=True, client_data=client_data)

        listener.assert_called_with(
            feature_name, is_enabled=True, client_data=client_data
        )


class TestGet(BaseTest):
    def test_returns_instance_of_feature_flag_class(self):
        feature_name = self.txt()

        self.client.create(feature_name)

        flag = self.client.get(feature_name)

        self.assertTrue(isinstance(flag, FeatureFlag))

    def test_returns_flag_with_correct_name(self):
        feature_name = self.txt()

        self.client.create(feature_name)

        flag = self.client.get(feature_name)

        self.assertEqual(feature_name, flag.name)


class TestDestroy(BaseTest):
    def test_get_will_return_instance_of_flag(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.destroy(feature_name)

        flag = self.client.get(feature_name)

        self.assertTrue(isinstance(flag, FeatureFlag))

    def test_status_switches_to_disabled(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.enable(feature_name)
        self.client.destroy(feature_name)

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.client.destroy(feature_name)

    def test_emits_pre_destroy_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.PRE_DESTROY, f=listener)

        self.client.events = events
        self.client.create(feature_name)
        self.client.destroy(feature_name)

        listener.assert_called_once_with(feature_name)

    def test_emits_post_destroy_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.POST_DESTROY, f=listener)

        self.client.events = events
        self.client.create(feature_name)
        self.client.destroy(feature_name)

        listener.assert_called_once_with(feature_name)


class TestEnable(BaseTest):
    def test_is_enabled_will_be_true(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.enable(feature_name)

        self.assertTrue(self.client.is_enabled(feature_name))

    def test_is_enabled_will_be_true_if_disable_was_called_earlier(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.disable(feature_name)
        self.client.enable(feature_name)

        self.assertTrue(self.client.is_enabled(feature_name))

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.client.enable(feature_name)

    def test_emits_pre_enable_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.PRE_ENABLE, f=listener)

        self.client.events = events
        self.client.create(feature_name)
        self.client.enable(feature_name)

        listener.assert_called_once_with(feature_name)

    def test_emits_post_enable_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.POST_ENABLE, f=listener)

        self.client.events = events
        self.client.create(feature_name)
        self.client.enable(feature_name)

        listener.assert_called_once_with(feature_name)


class TestDisable(BaseTest):
    def test_is_enabled_will_be_false(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.disable(feature_name)

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_is_enabled_will_be_false_if_enable_was_called_earlier(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.enable(feature_name)
        self.client.disable(feature_name)

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.client.disable(feature_name)

    def test_emits_pre_disable_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.PRE_DISABLE, f=listener)

        self.client.events = events
        self.client.create(feature_name)
        self.client.disable(feature_name)

        listener.assert_called_once_with(feature_name)

    def test_emits_post_disable_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.POST_DISABLE, f=listener)

        self.client.events = events
        self.client.create(feature_name)
        self.client.disable(feature_name)

        listener.assert_called_once_with(feature_name)


class TestExists(BaseTest):
    def test_exists_is_false_when_feature_does_not_exist(self):
        feature_name = self.txt()

        self.assertFalse(self.client.exists(feature_name))

    def test_exists_is_true_when_feature_does_exist(self):
        feature_name = self.txt()
        self.client.create(feature_name)

        self.assertTrue(self.client.exists(feature_name))


class TestList(BaseTest):
    def test_calls_backend_with_correct_args(self):
        self.store.list = MagicMock()

        limit, offset = 10, 25
        list(self.client.list(limit=limit, offset=offset))

        self.store.list.assert_called_once_with(limit=limit, offset=offset)

    def test_returns_flag_objects(self):
        feature_name = self.txt()

        self.client.create(feature_name)

        flag = next(self.client.list())

        self.assertIsInstance(flag, FeatureFlag)

    def test_returns_correct_flag_objects(self):
        feature_name = self.txt()

        expected = self.client.create(feature_name)

        actual = next(self.client.list())

        self.assertEqual(expected.name, actual.name)

    def test_returns_correct_count_of_flag_objects(self):
        feature_names = [self.txt() for _ in range(10)]

        for feature_name in feature_names:
            self.client.create(feature_name)

        actual = list(self.client.list())

        self.assertEqual(len(feature_names), len(actual))


class TestSetClientData(BaseTest):
    def test_calls_backend_with_correct_feature_name(self):
        self.store.set_meta = MagicMock()

        feature_name = self.txt()
        client_data = {self.txt(): self.txt()}

        self.client.create(feature_name)
        self.client.set_client_data(feature_name, client_data)

        [actual, _] = self.store.set_meta.call_args[0]

        self.assertEqual(feature_name, actual)

    def test_calls_backend_with_instance_of_meta(self):
        self.store.set_meta = MagicMock()

        feature_name = self.txt()
        client_data = {self.txt(): self.txt()}

        self.client.create(feature_name)
        self.client.set_client_data(feature_name, client_data)

        [_, meta] = self.store.set_meta.call_args[0]

        self.assertIsInstance(meta, FeatureFlagStoreMeta)

    def test_calls_backend_with_correct_meta_client_data(self):
        self.store.set_meta = MagicMock()

        feature_name = self.txt()
        client_data = {self.txt(): self.txt()}

        self.client.create(feature_name)
        self.client.set_client_data(feature_name, client_data)

        [_, meta] = self.store.set_meta.call_args[0]

        self.assertEqual(client_data, meta.client_data)

    def test_calls_backend_with_non_null_meta_created_date(self):
        self.store.set_meta = MagicMock()

        feature_name = self.txt()
        client_data = {self.txt(): self.txt()}

        self.client.create(feature_name)
        self.client.set_client_data(feature_name, client_data)

        [_, meta] = self.store.set_meta.call_args[0]

        self.assertIsNotNone(meta.created_date)

    def test_calls_backend_exactly_once(self):
        self.store.set_meta = MagicMock()

        feature_name = self.txt()
        client_data = {self.txt(): self.txt()}

        self.client.create(feature_name)
        self.client.set_client_data(feature_name, client_data)

        self.assertEqual(1, self.store.set_meta.call_count)

    def test_merges_new_values_with_existing(self):
        feature_name = self.txt()
        existing_data = {"existing_key": self.txt()}

        self.store.create(feature_name, client_data=existing_data)

        new_data = {"new_key": self.txt()}
        self.client.set_client_data(feature_name, new_data)

        item = self.store.get(feature_name)

        self.assertEqual({**existing_data, **new_data}, item.meta["client_data"])

    def test_can_override_existing_values(self):
        feature_name = self.txt()
        existing_data = {"existing_key": self.txt()}

        self.store.create(feature_name, client_data=existing_data)

        new_data = {"existing_key": self.txt(), "new_key": self.txt()}
        self.client.set_client_data(feature_name, new_data)

        item = self.store.get(feature_name)

        self.assertEqual(new_data, item.meta["client_data"])

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()
        client_data = {self.txt(): self.txt()}

        with self.assertRaises(FlagDoesNotExistError):
            self.client.set_client_data(feature_name, client_data)

    def test_emits_pre_set_client_data_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.PRE_SET_CLIENT_DATA, f=listener)

        existing_data = {"existing_key": self.txt()}

        self.client.events = events
        self.client.create(feature_name, client_data=existing_data)

        new_data = {"existing_key": self.txt(), "new_key": self.txt()}
        self.client.set_client_data(feature_name, new_data)

        listener.assert_called_once_with(feature_name, new_data)

    def test_emits_post_set_client_data_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.POST_SET_CLIENT_DATA, f=listener)

        existing_data = {"existing_key": self.txt()}

        self.client.events = events
        self.client.create(feature_name, client_data=existing_data)

        new_data = {"existing_key": self.txt(), "new_key": self.txt()}
        self.client.set_client_data(feature_name, new_data)

        listener.assert_called_once_with(feature_name, new_data)


class TestGetClientData(BaseTest):
    def test_gets_expected_key_value_pairs(self):
        feature_name = self.txt()
        client_data = {self.txt(): self.txt()}

        self.client.create(feature_name, client_data=client_data)

        result = self.client.get_client_data(feature_name)

        self.assertEqual(client_data, result)

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.client.get_client_data(feature_name)


class TestGetMeta(BaseTest):
    def test_includes_created_date(self):
        feature_name = self.txt()
        client_data = {self.txt(): self.txt()}

        self.client.create(feature_name, client_data=client_data)

        meta = self.client.get_meta(feature_name)

        self.assertTrue("created_date" in meta)

    def test_includes_client_data(self):
        feature_name = self.txt()
        client_data = {self.txt(): self.txt()}

        self.client.create(feature_name, client_data=client_data)

        meta = self.client.get_meta(feature_name)

        self.assertEqual(client_data, meta["client_data"])

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.client.get_meta(feature_name)


class TestAddCondition(BaseTest):
    def test_condition_gets_included_in_meta(self):
        feature_name = self.txt()
        condition_checks = {self.txt(): True}
        condition = Condition(**condition_checks)

        self.client.create(feature_name)
        self.client.add_condition(feature_name, condition)

        meta = self.client.get_meta(feature_name)

        self.assertTrue(condition.to_dict() in meta["conditions"])

    def test_condition_gets_appended_to_meta(self):
        feature_name = self.txt()
        condition_checks = {self.txt(): True}
        condition = Condition(**condition_checks)

        self.client.create(feature_name)
        self.client.add_condition(feature_name, condition)
        self.client.add_condition(feature_name, condition)

        meta = self.client.get_meta(feature_name)

        self.assertEqual(2, len(meta["conditions"]))

    def test_emits_pre_add_condition_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.PRE_ADD_CONDITION, f=listener)

        condition_checks = {self.txt(): True}
        condition = Condition(**condition_checks)

        self.client.events = events
        self.store.create(feature_name)
        self.client.add_condition(feature_name, condition)

        listener.assert_called_once_with(feature_name, condition)

    def test_emits_post_add_condition_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.POST_ADD_CONDITION, f=listener)

        condition_checks = {self.txt(): True}
        condition = Condition(**condition_checks)

        self.client.events = events
        self.store.create(feature_name)
        self.client.add_condition(feature_name, condition)

        listener.assert_called_once_with(feature_name, condition)


class TestSetBucketer(BaseTest):
    def test_bucketer_gets_included_in_meta(self):
        feature_name = self.txt()

        percentage_value = 0.1
        bucketer = PercentageBucketer(percentage=Percentage(percentage_value))

        self.client.create(feature_name)
        self.client.set_bucketer(feature_name, bucketer)

        meta = self.client.get_meta(feature_name)

        self.assertEqual(bucketer.to_dict(), meta["bucketer"])

    def test_emits_pre_set_bucketer_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.PRE_SET_BUCKETER, f=listener)

        percentage_value = 0.1
        bucketer = PercentageBucketer(percentage=Percentage(percentage_value))

        self.client.events = events
        self.store.create(feature_name)
        self.client.set_bucketer(feature_name, bucketer)

        listener.assert_called_once_with(feature_name, bucketer)

    def test_emits_post_set_bucketer_event(self):
        feature_name = self.txt()
        events = FlipperEventEmitter()

        listener = MagicMock()

        events.on(EventType.POST_SET_BUCKETER, f=listener)

        percentage_value = 0.1
        bucketer = PercentageBucketer(percentage=Percentage(percentage_value))

        self.client.events = events
        self.store.create(feature_name)
        self.client.set_bucketer(feature_name, bucketer)

        listener.assert_called_once_with(feature_name, bucketer)


class TestSetConditions(BaseTest):
    class Subscriber(FlipperEventSubscriber):
        def __init__(self) -> None:
            super().__init__()
            self.events = []  # type: List[Tuple[str, str, Iterable[Condition]]]

        def on_pre_set_conditions(self, flag_name: str, conditions):
            self.events.append(("pre_set_conditions", flag_name, conditions))

        def on_post_set_conditions(self, flag_name: str, conditions):
            self.events.append(("post_set_conditions", flag_name, conditions))

    def setUp(self):
        super().setUp()
        self.subscriber = self.Subscriber()
        self.client.events.register_subscriber(self.subscriber)

    def test_overrides_previous_conditions(self):
        feature_name = "FLAG"
        overriden_condition = Condition(value=True)
        new_conditions = [Condition(new_value=True), Condition(id__in=[1, 2])]
        self.client.create(feature_name)

        self.client.add_condition(feature_name, overriden_condition)
        self.client.set_conditions(feature_name, new_conditions)

        conditions_array = self.client.get_meta(feature_name)["conditions"]
        expected_conditions_array = [
            {"new_value": [{"variable": "new_value", "value": True, "operator": None}]},
            {"id": [{"variable": "id", "value": [1, 2], "operator": "in"}]},
        ]

        self.assertEqual(expected_conditions_array, conditions_array)

    def test_events_are_emitted(self):
        feature_name = "FLAG"
        new_conditions = [Condition(new_value=True), Condition(id__in=[1, 2])]

        self.client.create(feature_name)

        self.client.set_conditions(feature_name, new_conditions)
        assert self.subscriber.events == [
            ("pre_set_conditions", feature_name, new_conditions),
            ("post_set_conditions", feature_name, new_conditions),
        ]
