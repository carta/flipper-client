from typing import Callable, Optional

from .client import FeatureFlagClient


def is_enabled(
    flags: FeatureFlagClient, feature_name: str, redirect: Optional[Callable] = None
):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            if flags.is_enabled(feature_name):
                return fn(*args, **kwargs)
            if redirect is None:
                return
            return redirect(*args, **kwargs)

        return wrapper

    return decorator
