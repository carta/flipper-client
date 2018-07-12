Flipper
=======
![Circle CI Status](https://circleci.com/gh/carta/flipper-client/tree/master.svg?style=shield&circle-token=e401445db3e99e8fac7555bd9ba5040e6a2eb4bd)

Flipper is Carta's feature flagging tool. This is the client library.

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

**`create(feature_name: str, is_enabled: bool=False, client_data: dict=None) -> FeatureFlag`**

Create a new feature flag and optionally set value (is_enabled is false/disabled).

For advanced implementations, you can also specify user-defined key-value pairs as a `dict` via the client_data keyword argument. These values should be json serializable and will be stored in the metadata section of the flag object.

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

**`set_client_data(feature_name: str, client_data: dict) -> void`**

Set key-value pairs to be stored as metadata with the flag. Can be retrieved using `get_client_data`. This will merge the supplied values with anything that already exists.

Example:

```python
features.set_client_data(MY_FEATURE, { 'ttl': 3600 })
```

**`get_client_data(feature_name: str) -> dict`**

Retrieve key-value any key-value pairs stored in the metadata for this flag.

Example:

```python
features.get_client_data(MY_FEATURE)
```

**`get_meta(feature_name: str) -> dict`**

Similar to `get_client_data` but instead of returning onlu client-supplied metadata, it will return all metadata for the flag, including system-set values such as `created_date`.

Example:

```python
features.get_meta(MY_FEATURE)
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

**`set_client_data(client_data: dict) -> void`**

Set key-value pairs to be stored as metadata with the flag. Can be retrieved using `get_client_data`. This will merge the supplied values with anything that already exists.

Example:

```python
flag.set_client_data({ 'ttl': 3600 })
```

**`get_client_data() -> dict`**

Retrieve key-value any key-value pairs stored in the metadata for this flag.

Example:

```python
flag.get_client_data()
```

**`get_meta() -> dict`**

Similar to `get_client_data` but instead of returning onlu client-supplied metadata, it will return all metadata for the flag, including system-set values such as `created_date`.

Example:

```python
flag.get_meta()
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
- `ThriftRPCFeatureFlagStore` (Requires a server that implements the `FeatureFlagStore` thrift service)


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

## Usage with a Thrift RPC server

If you would like to manage feature flags with a custom service that is possible by using the `ThriftRPCFeatureFlagStore` backend. To do this, you will need to implement the `FeatureFlagStore` service defined in `thrift/feature_flag_store.thrift`. Then when you intialize the `ThriftRPCFeatureFlagStore` you will need to pass an instance of a compatible thrift client.

First, install the `thrift` package:

```
pip install thrift
```

Example:

```python
from flipper import FeatureFlagClient, ThriftRPCFeatureFlagStore
from flipper_thrift.python.feature_flag_store import (
    FeatureFlagStore as TFeatureFlagStore
)
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


transport = TSocket.TSocket('localhost', 9090)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

thrift_client = TFeatureFlagStore.Client(protocol)

transport.open()

store = ThriftRPCFeatureFlagStore(thrift_client)
client = FeatureFlagClient(store)
```

*Note: this can also be optimized with the `CachedFeatureFlagStore`. See the redis examples above.*

You will also be required to implement the server, like so:

```python
import re

from flipper_thrift.python.feature_flag_store import (
    FeatureFlagStore as TFeatureFlagStore
)
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer


class FeatureFlagStoreServer(object):
    # Convert TitleCased calls like .Get() to snake_case calls like .get()
    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return object.__getattribute__(self, self._convert_case(attr))

    def _convert_case(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def create(self, feature_name, is_enabled):
        pass
    def delete(self, feature_name):
        pass
    def get(self, feature_name):
        return True
    def set(self, feature_name, is_enabled):
        pass

if __name__ == '__main__':
    server = FeatureFlagStoreServer()
    processor = TFeatureFlagStore.Processor(server)
    transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    TServer.TSimpleServer(processor, transport, tfactory, pfactory)
```

# Creating a custom backend

Don't see the backend you like? You can easily implement your own. If you define a class that implements the `AbstractFeatureFlagStore` interface, located in `flipper.contrib.store` then you can pass an instance of it to the `FeatureFlagClient` constructor.

Pull requests welcome.

# Development

Clone the repo and run `pip install -e .[dev]` to get the environment set up. Test are run with the `pytest` command.


## Building thrift files

First, [install the thrift compiler](https://thrift.apache.org/tutorial/). On mac, the easiest way is to use homebrew:

```
brew install thrift
```

Then simply run `make thrift`. Remember to commit the results of the compilation step.
