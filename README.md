# Quickstart

`pip install flipper`


```python
from flipper import FeatureFlagClient, MemoryFeatureFlagStore


features = FeatureFlagClient(MemoryFeatureFlagStore())

MY_FEATURE = 'MY_FEATURE'

features.create(MY_FEATURE)
features.enable(MY_FEATURE)

if features.is_enabled(MY_FEATURE):
    run_my_feature()
else:
    run_old_feature()
```

# API

## FeatureFlagClient

**`is_enabled(feature_name: str) -> bool`**

Check if a feature is enabled

Example:

```python
features.is_enabled(MY_FEATURE)
```

**`create(feature_name: str, default: bool=False) -> FeatureFlag`**

Create a new feature flag and optionally set value (default is false/disabled)

Example:

```python
flag = features.create(MY_FEATURE)
```

**`get(feature_name: str) -> FeatureFlag`**

Returns an instance of `FeatureFlag` for the requested flag.

Example:

```python
flag = features.get(MY_FEATURE)
```

**`enable(feature_name: str) -> void`**

Enables the specified flag. Subsequent calls to `is_enabled` should return true.

Example:

```python
features.enable(MY_FEATURE)
```

**`disable(feature_name: str) -> void`**

Disables the specified flag. Subsequent calls to `is_enabled` should return false.

Example:

```python
features.disable(MY_FEATURE)
```

**`destroy(feature_name: str) -> void`**

Destroys the specified flag. Subsequent calls to `is_enabled` should return false.

Example:

```python
features.destroy(MY_FEATURE)
```

## FeatureFlagClient

**`is_enabled() -> bool`**

Check if a feature is enabled

Example:

```python
flag.is_enabled()
```

**`enable() -> void`**

Enables the flag. Subsequent calls to `is_enabled` should return true.

Example:

```python
flag.enable()
```

**`disable() -> void`**

Disables the specified flag. Subsequent calls to `is_enabled` should return false.

Example:

```python
flag.disable()
```

**`destroy() -> void`**

Destroys the flag. Subsequent calls to `is_enabled` should return false.

Example:

```python
flag.destroy()
```

## decorators

**`is_enabled(features: FeatureFlagClient, feature_name: str, redirect: Optional[Callable]=None)`**

This is a decorator that can be used on any function (including django/flask views). If the feature is enabled then the function will be called. If the feature is not enabled, the function will not be called. If a callable `redirect` function is provided, then the `redirect` function will be called instead when the feature is not enabled.

Example:

```python
from flipper.decorators import is_enabled

from myapp.feature_flags import (
    FEATURE_IMPROVED_HORSE_SOUNDS,
    features,
)


@is_enabled(
    features.instance,
    FEATURE_IMPROVED_HORSE_SOUNDS,
    redirect=old_horse_sound,
)
def new_horse_sound(request):
    return HttpResponse('Whinny')

def old_horse_sound(request):
    return HttpResponse('Neigh')
```

# Initialization

flipper is designed to provide a common interface that is agnostic to the storage backend you choose. To create a client simply import the `FeatureFlagClient` class and your storage backend of choice.

Out of the box, we support the following backends:

- `MemoryFeatureFlagStore` (an in-memory store useful for development and tests)
- `ConsulFeatureFlagStore` (Requires a running consul cluster. Provides the lowest latency of all the options)
- `RedisFeatureFlagStore` (Requires a running redis cluster. Can be combined with `CachedFeatureFlagStore` to reduce average latency.)


## Usage with in-memory backend

This backend is useful for unit tests or development environments where you don't require data durability. It is the simplest of the stores.

```python
from flipper import FeatureFlagClient, MemoryFeatureFlagStore


client = FeatureFlagClient(MemoryFeatureFlagStore())
```

## Usage with Consul backend

[consul](https://www.consul.io/intro/index.html), among other things, is a key-value storage system with an easy to use interface. The consul backend maintains a persistent connection to your consul cluster and watches for changes to the base key you specify. For example, if your base key is `features`, it will look for changes to any key one level beneath. This means that the consul backend has lower latency than the other supported backends.

```python
import consul
from flipper import ConsulFeatureFlagStore, FeatureFlagClient


c = consul.Consul(host='127.0.0.1', port=32769)

# default base_key is 'features'
store = ConsulFeatureFlagStore(c, base_key='feature-flags')
client = FeatureFlagClient(store)
```

## Usage with Redis backend

To connect flipper to redis just create an instance of `StrictRedis` and supply it to the `RedisFeatureFlagStore` backend. Features will be tracked under the base key your provide (default is `features`).

Keep in mind, this will do a network call every time a feature flag is checked, so you may want to add a local in-memory cache (see below).


```python
import redis
from flipper import FeatureFlagClient, RedisFeatureFlagStore


r = redis.StrictRedis(host='localhost', port=6379, db=0)

# default base_key is 'features'
store = RedisFeatureFlagStore(r, base_key='feature-flags')
client = FeatureFlagClient(store)
```

## Usage with Redis backend and in-memory cache

To reduce the average network latency associated with storing feature flags in a remote redis cluster, you can wrap the `RedisFeatureFlagStore` in `CachedFeatureFlagStore`. This class takes a `FeatureFlagStore` as an argument at initialization. When the client checks a flag, it will first look in its local cache, and if it cannot find a value for the specified feature, it will look in Redis. When a value is retrieved from Redis, it will be inserted into the local cache for quick retrieval. The cache is implemented as an LRU cache, and it has a default expiration time of 15 minutes. To customize the expiration, or any other of the [cache properties](https://github.com/stucchio/Python-LRU-cache), simply pass them as keyworkd arguments to the `CachedFeatureFlagStore` constructor.


```python
import redis
from flipper import (
    CachedFeatureFlagStore,
    FeatureFlagClient,
    RedisFeatureFlagStore,
)


r = redis.StrictRedis(host='localhost', port=6379, db=0)

store = RedisFeatureFlagStore(r)

# For all cache options, see:
# https://github.com/stucchio/Python-LRU-cache
# Expiration defaults to 
cache = CachedFeatureFlagStore(redis, expiration=30)

client = FeatureFlagClient(cache)
```

# Creating a custom backend

Don't see the backend you like? You can easily implement your own. If you define a class that implements the `AbstractFeatureFlagStore` interface, located in `flipper.contrib.store` then you can pass an instance of it to the `FeatureFlagClient` constructor.

Pull requests welcome.

# Development

Clone the repo and run `pip install -e .` to get the environment set up. Test are run with the `pytest` command.
