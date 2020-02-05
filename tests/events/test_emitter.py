from unittest.mock import MagicMock

import pytest

from flipper.events import EventType, FlipperEventEmitter, FlipperEventSubscriber


class DummySubscriber(FlipperEventSubscriber):
    def __init__(self, mock):
        self._mock = mock

    def on_pre_create(self, *args, **kwargs):
        self._mock.on_pre_create(*args, **kwargs)

    def on_post_create(self, *args, **kwargs):
        self._mock.on_post_create(*args, **kwargs)

    def on_pre_enable(self, *args, **kwargs):
        self._mock.on_pre_enable(*args, **kwargs)

    def on_post_enable(self, *args, **kwargs):
        self._mock.on_post_enable(*args, **kwargs)

    def on_pre_disable(self, *args, **kwargs):
        self._mock.on_pre_disable(*args, **kwargs)

    def on_post_disable(self, *args, **kwargs):
        self._mock.on_post_disable(*args, **kwargs)

    def on_pre_destroy(self, *args, **kwargs):
        self._mock.on_pre_destroy(*args, **kwargs)

    def on_post_destroy(self, *args, **kwargs):
        self._mock.on_post_destroy(*args, **kwargs)

    def on_pre_add_condition(self, *args, **kwargs):
        self._mock.on_pre_add_condition(*args, **kwargs)

    def on_post_add_condition(self, *args, **kwargs):
        self._mock.on_post_add_condition(*args, **kwargs)

    def on_pre_set_conditions(self, *args, **kwargs):
        self._mock.on_pre_set_conditions(*args, **kwargs)

    def on_post_set_conditions(self, *args, **kwargs):
        self._mock.on_post_set_conditions(*args, **kwargs)

    def on_pre_set_client_data(self, *args, **kwargs):
        self._mock.on_pre_set_client_data(*args, **kwargs)

    def on_post_set_client_data(self, *args, **kwargs):
        self._mock.on_post_set_client_data(*args, **kwargs)

    def on_pre_set_bucketer(self, *args, **kwargs):
        self._mock.on_pre_set_bucketer(*args, **kwargs)

    def on_post_set_bucketer(self, *args, **kwargs):
        self._mock.on_post_set_bucketer(*args, **kwargs)


class TestRegisterSubscriber:
    @pytest.mark.parametrize("event_type", list(EventType))
    def test_all_listeners_get_registered(self, event_type):
        mock = MagicMock()
        subscriber = DummySubscriber(mock)
        events = FlipperEventEmitter()
        events.register_subscriber(subscriber)
        events.emit(event_type)
        getattr(mock, "on_%s" % event_type.value).assert_called_once_with()


class TestRemoveSubscriber:
    @pytest.mark.parametrize("event_type", list(EventType))
    def test_all_listeners_get_removed(self, event_type):
        mock = MagicMock()
        subscriber = DummySubscriber(mock)
        events = FlipperEventEmitter()
        events.register_subscriber(subscriber)
        events.remove_subscriber(subscriber)
        events.emit(event_type)
        getattr(mock, "on_%s" % event_type.value).assert_not_called()
