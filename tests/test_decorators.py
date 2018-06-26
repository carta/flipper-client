import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import FeatureFlagClient, MemoryFeatureFlagStore, decorators


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.store = MemoryFeatureFlagStore()
        self.client = FeatureFlagClient(self.store)
        self.feature_name = self.txt()
        self.flag = self.client.create(self.feature_name)

    def txt(self):
        return uuid4().hex


class TestIsEnabled(BaseTest):
    def test_calls_method_when_is_enabled_is_true(self):
        _mock = MagicMock()

        @decorators.is_enabled(self.client, self.feature_name)
        def method(*args, **kwargs):
            return _mock(*args, **kwargs)

        self.flag.enable()

        args = (1, 2, 3)

        method(*args)

        _mock.assert_called_once_with(*args)

    def test_method_not_called_when_is_enabled_is_false(self):
        _mock = MagicMock()

        @decorators.is_enabled(self.client, self.feature_name)
        def method(*args, **kwargs):
            return _mock(*args, **kwargs)

        self.flag.disable()

        method()

        _mock.assert_not_called()

    def test_redirects_when_feature_disabled_and_redirect_supplied(self):
        redirect_to = MagicMock()

        @decorators.is_enabled(self.client, self.feature_name, redirect=redirect_to)
        def method(*args, **kwargs):
            return

        self.flag.disable()

        args = (1, 2, 3)

        method(*args)

        redirect_to.assert_called_once_with(*args)

    def test_does_not_redirect_when_feature_enabled(self):  # noqa: E501
        redirect_to = MagicMock()

        @decorators.is_enabled(self.client, self.feature_name, redirect=redirect_to)
        def method(*args, **kwargs):
            return

        self.flag.enable()

        method()

        redirect_to.assert_not_called()
