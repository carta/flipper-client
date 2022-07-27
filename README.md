Flipper
=======
![Circle CI Status](https://circleci.com/gh/carta/flipper-client/tree/master.svg?style=shield&circle-token=e401445db3e99e8fac7555bd9ba5040e6a2eb4bd)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Flipper is a lightweight, easy to use, and flexible library for feature flags in python. It is intended to allow developers to push code to production in a disabled state and carefully control whether or not the code is enabled or disabled without doing additional releases.

# Quickstart

`pip install flipper-client`


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

**`is_enabled(feature_name: str, **conditions) -> bool`**

Check if a feature is enabled. Also supports conditional enabling of features. To check for conditionally enabled features, pass keyword arguments with conditions you wish to supply. For more information, see the conditions section.

Example:

```python
features.is_enabled(MY_FEATURE)

# With conditons
features.is_enabled(FEATURE_IMPROVED_HORSE_SOUNDS, is_horse_lover=True)
```

**`create(feature_name: str, is_enabled: bool=False, client_data: dict=None) -> FeatureFlag`**

Create a new feature flag and optionally set value (is_enabled is false/disabled).

For advanced implementations, you can also specify user-defined key-value pairs as a `dict` via the client_data keyword argument. These values should be json serializable and will be stored in the metadata section of the flag object.

Example:

```python
flag = features.create(MY_FEATURE)
```

**`exists(feature_name: str) -> bool`**

Check if a feature flag already exists by name. Feature flag names must be unique.

Example:

```python
 if not features.exists(MY_FEATURE):
    features.create(MY_FEATURE)
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

**`list(limit: Optional[int] = None, offset: int = 0) -> Iterator[FeatureFlag]`**

Lists all flags subject to the limit and offset you provide. The results are not guaranteed to be in order. Ordering depends on the backend you choose so plan accordingly.

Example:

```python
for feature in features.list(limit=100):
    print(feature.name, feature.is_enabled())
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

Similar to `get_client_data` but instead of returning only client-supplied metadata, it will return all metadata for the flag, including system-set values such as `created_date`.

Example:

```python
features.get_meta(MY_FEATURE)
```

**`add_condition(feature_name: str, condition: Condition) -> void`**

Adds a condition to for enabled checks, such that `is_enabled` will only return true if all the conditions are satisfied when it is called.

Example:

```python
from flipper import Condition


features.add_condition(MY_FEATURE, Condition(is_administrator=True))

features.is_enabled(MY_FEATURE, is_administrator=True) # returns True
features.is_enabled(MY_FEATURE, is_administrator=False) # returns False

```

**`set_bucketer(feature_name: str, bucketer: Bucketer) -> void`**

Set the bucketer that used to bucket requests based on the checks passed to `is_enabled`. This is useful if you want to segment your traffic based on percentages or other heuristics that cannot be enforced with `Condition`s. See the `Bucketing` section for more details.

```python
from flipper.bucketing import Percentage, PercentageBucketer


# Create a bucketer that will randomly enable a feature for 10% of traffic
bucketer = PercentageBucketer(percentage=Percentage(0.1))

client.set_bucketer(MY_FEATURE, bucketer)

client.is_enabled(MY_FEATURE) # returns False 90% of the time
```

## FeatureFlag

**`is_enabled() -> bool`**

Check if a feature is enabled. Also supports conditional enabling of features. To check for conditionally enabled features, pass keyword arguments with conditions you wish to supply. For more information, see the conditions section.

Example:

```python
flag.is_enabled()

# With conditons
flag.is_enabled(is_horse_lover=True, horse_type__in=['Stallion', 'Mare'])
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

Similar to `get_client_data` but instead of returning only client-supplied metadata, it will return all metadata for the flag, including system-set values such as `created_date`.

Example:

```python
flag.get_meta()
```

**`add_condition(condition: Condition) -> void`**

Adds a condition to for enabled checks, such that `is_enabled` will only return true if all the conditions are satisfied when it is called.

Example:

```python
from flipper import Condition


flag.add_condition(Condition(is_administrator=True))

flag.is_enabled(is_administrator=True)  # returns True
flag.is_enabled(is_administrator=False)  # returns False
```

**`set_bucketer(bucketer: Bucketer) -> void`**

Set the bucketer that used to bucket requests based on the checks passed to `is_enabled`. This is useful if you want to segment your traffic based on percentages or other heuristics that cannot be enforced with `Condition`s. See the `Bucketing` section for more details.

```python
from flipper.bucketing import Percentage, PercentageBucketer


# Create a bucketer that will enable a feature for 10% of traffic
bucketer = PercentageBucketer(percentage=Percentage(0.1))

flag.set_bucketer(bucketer)

flag.is_enabled() # returns False 90% of the time
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

## Conditions

Flipper supports conditionally enabled feature flags. These are useful if you want to enable a feature for a subset of users or based on some other condition within your application. Its usage is very simple. First, import the `Condition` class:


```python
from flipper import Condition
```

Then add the condition to a flag using the `add_condition` method of the `FeatureFlagClient` or `FeatureFlag` interface. You can add as many conditions as you like, and each condition may specify multiple checks:


```python
flag = client.get(FEATURE_IMPROVED_HORSE_SOUNDS)

# Feature is only enabled for horse lovers
flag.add_condition(Condition(is_horse_lover=True))

# Feature is only enabled for people with more than 9000 horses who don't live in the city
flag.add_condition(Condition(number_of_horses_owned__gt=9000, location__ne='city'))
```

Then you can specify these checks when calling `is_enabled`. The checks are not required, and if not specified `is_enabled` will return the base `enabled` status of the feature.

```python
flag.enable()
flag.is_enabled()  # True
flag.is_enabled(is_horse_lover=True)  # True
flag.is_enabled(is_horse_lover=True, number_of_horses_owned=8000)  # False
flag.is_enabled(location='city')  # False
```

### Condition operators supported

In addition to equality conditions, `Conditions` support the following operator comparisons:

- `__gt` Greater than
- `__gte` Greater than or equal to
- `__lt` Less than
- `__lte` Less than or equal to
- `__ne` Not equals
- `__in` Set membership
- `__not_in` Set non-membership

Operators must be a suffix of the argument name and must include `__`.

## Bucketing

Bucketing is useful if you ever want the result of `is_enabled` to vary depending on a pre-defined percentage value. Examples might include A/B testing or canary releases. Out of the box, flipper supports percentage-based bucketing for both random-assignment cases and consistent-assignment cases. Flipper also supports linear ramps for variable percentage cases.

Conditions always take precedence over bucketing when applied together.

### Random assignment

This is the simplest possible bucketing scenario, where you want to randomly segment traffic using a constant percentage.

```python
from flipper.bucketing import Percentage, PercentageBucketer

from myapp import features


FEATURE_NAME = 'HOMEPAGE_AB_TEST'

flag = features.create(FEATURE_NAME)

bucketer = PercentageBucketer(Percentage(0.5))

flag.set_bucketer(bucketer)
flag.enable()  # global enabled status overrides buckets

flag.is_enabled()  # has a 50% shot of returning True each time it is called
```

### Consistent assignment

This mechanism works like percentage-based bucket assignment, except the bucketer will always return the same value for the values it is provided. In other words, if you pass the same keyword arguments to `is_enabled` it will always return the same result for those arguments. This works using consistent hashing of the keyword arguments. The keyword arguments get serialized as json and hashed. This hash is then mod-ded by 100 to give a value in the range 0-100. This value is then compared to the current percentage to derminine whether or not that bucket is enabled.

When is this useful? Any time you want to randomize traffic, but you want each individual client/user to always receive the same experience.

This is perhaps easisest to illustrate with and example:

```python
from flipper.bucketing import Percentage, ConsistentHashPercentageBucketer

from myapp import features


FEATURE_NAME = 'HOMEPAGE_AB_TEST'

flag = features.create(FEATURE_NAME)

bucketer = ConsistentHashPercentageBucketer(
    key_whitelist=['user_id'],
    percentage=Percentage(0.5),
)

flag.set_bucketer(bucketer)
flag.enable()  # global enabled status overrides buckets

flag.is_enabled(user_id=1) # Always returns True (bucket is 0.48)
flag.is_enabled(user_id=2) # Always returns False (bucket is 0.94)
```

#### Combining with Conditions

These can also be combined with conditions. When a bucketer is combined with one or more conditions, the conditions take precedence. That is, if any of the conditions evaluate to `False`, then `is_enabled` will return `False` regardless of what the bucketing status is. The converse also holds: If if all of the conditions evaluate to `True`, then `is_enabled` will return `True` regardless of what the bucketing status is.

However, if no keyword arguments that match current conditions are supplied to `is_enabled`, any conditions will evaluate to `True`.

```python
bucketer = ConsistentHashPercentageBucketer(
    key_whitelist=['user_id'],
    percentage=Percentage(0.5),
)
condition = Condition(is_admin=True)

# This will enable the flag for 50% of traffic and all administrators
flag.enable()
flag.add_condition(condition)
flag.set_bucketer(bucketer)

flag.is_enabled(user_id=2) # False
flag.is_enabled(user_id=2, is_admin=True) # True

flag.is_enabled(user_id=1) # True
flag.is_enabled(user_id=1, is_admin=False) # False
```

#### Key whitelists

If you want bucketers to inspect a subset of the keyword arguments that `is_enabled` receives, use the `key_whitelist` parameter when initializing the `ConsistentHashPercentageBucketer`.

```python
bucketer = ConsistentHashPercentageBucketer(
    key_whitelist=['user_id'],
    percentage=Percentage(0.5),
)
condition = Condition(number_of_horses_owned__lt=9000)

flag.enable()
flag.set_bucketer(bucketer)

# Ignore all keys except user_id
flag.is_enabled(user_id=1, number_of_horses_owned=9001)  # True
```

### Ramping percentages over time

If you want to increase or decrease the percentage value over time, you can use the `LinearRampPercentage` class. This class takes the following parameters:

- `initial_value: float=0.0`: The starting percentage
- `final_value: float=1.0`: The ending percentage
- `ramp_duration: int=3600`: The time (in seconds) for the ramp to complete
- `initial_time: Optional[int]=now()`: The timestamp of when the ramp "started". Not common. Defaults to now.

This class can be used anywhere you would use a `Percentage`:


```python
from flipper.bucketing import LinearRampPercentage, PercentageBucketer

from myapp import features


FEATURE_NAME = 'HOMEPAGE_AB_TEST'

flag = features.create(FEATURE_NAME)

# Ramp from 20% to 80% over 30 minutes
bucketer = PercentageBucketer(
    percentage=LinearRampPercentage(
        initial_value=0.2,
        final_value=0.8,
        ramp_duration=1800,
    ),
)

flag.set_bucketer(bucketer)
flag.enable()  # global enabled status overrides buckets

flag.is_enabled()  # has ≈ 0% chance

# Wait 10 minutes
flag.is_enabled() # has ≈ 33% chance

# Wait another 10 minutes
flag.is_enabled() # has ≈ 67% chance

# Wait another 10 minutes
flag.is_enabled() # has 100% chance
```

It works with `ConsistentHashPercentageBucketer` as well.

# Initialization

flipper is designed to provide a common interface that is agnostic to the storage backend you choose. To create a client simply import the `FeatureFlagClient` class and your storage backend of choice.

Out of the box, we support the following backends:

- `MemoryFeatureFlagStore` (an in-memory store useful for development and tests)
- `ConsulFeatureFlagStore` (Requires a running consul cluster. Provides the lowest latency of all the options)
- `RedisFeatureFlagStore` (Requires a running redis cluster. Can be combined with `CachedFeatureFlagStore` to reduce average latency.)
- `ThriftRPCFeatureFlagStore` (Requires a server that implements the `FeatureFlagStore` thrift service)
- `PostgreSQLFeatureFlagStore` (Requires a running postgreSQL server)


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

To connect flipper to redis just create an instance of `Redis` and supply it to the `RedisFeatureFlagStore` backend. Features will be tracked under the base key your provide (default is `features`).

Keep in mind, this will do a network call every time a feature flag is checked, so you may want to add a local in-memory cache (see below).


```python
import redis
from flipper import FeatureFlagClient, RedisFeatureFlagStore


r = redis.Redis(host='localhost', port=6379, db=0)

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


r = redis.Redis(host='localhost', port=6379, db=0)

store = RedisFeatureFlagStore(r)

# Cache options are:
# size (number of items to store, default=5000)
# ttl (seconds before key expires, default=None, i.e. No expiration)
cache = CachedFeatureFlagStore(store, ttl=30)

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

## Usage with Replicated backend

The `ReplicatedFeatureFlagStore` is meant for cases where you have a primary store and one or more secondary stores that you want to replicate your writes to. For example, if you wanted to write to redis, but also record these writes to an auditing system somewhere else.

This store takes a primary store, which must be an instance of `AbstractFeatureFlagStore`, and then 0 or more other instances to act as the replicas.

When you do any write operations, such as `create`, `set`, `delete`, or `set_meta`, these actions are first performed on the primary store, and then repeated on each of the secondary stores. **Important: no attempt is made to provide transaction-style consistency or rollbacks across writes**. Read operations will always pull from the primary store.

By default, the write operations are replicated asynchronously. To replicate synchronously, pass `asynch=False` to any of the methods.


```python
import redis
from flipper import (
    FeatureFlagClient,
    RedisFeatureFlagStore,
    ReplicatedFeatureFlagStore,
)


primary_redis = redis.Redis(host='localhost', port=6379, db=0)
backup_redis = redis.Redis(host='localhost', port=6379, db=1)

primary = RedisFeatureFlagStore(primary_redis, base_key='feature-flags')
replica = RedisFeatureFlagStore(backup_redis, base_key='feature-flags')

store = ReplicatedFeatureFlagStore(primary, replica)

client = FeatureFlagClient(store)
```

## Usage with S3 backend

To store flag data in S3, use the `S3FeatureFlagStore`. Simply create the bucket, initialize a `boto3` (not `boto`) S3 client, and launch an instance of `S3FeatureFlagStore`, passing the client and the bucket name. The store will write to the root of the bucket using the flag name as the object key. For example usage, take a look at the tests. For more information on working with boto3, see [the documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html).

Keep in mind that S3 is not an ideal choice for a production backend due to higher latency when compared to something like redis. However, it can be useful when used with [`ReplicatedFeatureFlagStore`](#usage-with-replicated-backend) as a replica for cold storage and backups. That way if your hot storage gets wiped out you have a backup or if you need an easy way to copy all the feature flag data it can be retrieved from S3.


```python
import boto3
from flipper import FeatureFlagClient, S3FeatureFlagStore


s3 = boto3.client('s3')

store = S3FeatureFlagStore(s3, 'my-flipper-bucket')

client = FeatureFlagClient(store)
```

## Usage with a PostgreSQL backend
To store flag data in a PostgreSQL database, use the `PostgreSQLFeatureFlagStore`.
To use, pass the connection string to the database as an argument.
Optional keyword arguments are: a `table_name `for the flag data (default is `feature_flags`), a `item_column` for the items' column identifier (default is `item`) and a `name_column` for the feature flag names' column identifier (default is `name`).
Optionally, you may choose not to run the database migrations on class instantiation by passing False to the keyword argument `run_migrations`. This can be useful when managing the schema manually or in cases where you want to wait for the postgres server.

```python
from flipper import FeatureFlagClient, PostgreSQLFeatureFlagStore


conninfo = "postgresql://user:secret@localhost"

store = PostgreSQLFeatureFlagStore(conninfo, table_name='my-flipper-table')

## Running migrations manually
store = PostgreSQLFeatureFlagStore(conninfo, table_name='my-flipper-table', run_migrations=False)
store.run_migrations()

client = FeatureFlagClient(store)
```

# Creating a custom backend

Don't see the backend you like? You can easily implement your own. If you define a class that implements the `AbstractFeatureFlagStore` interface, located in `flipper.contrib.store` then you can pass an instance of it to the `FeatureFlagClient` constructor.

Pull requests welcome.

# Events

Flipper ships with a system for hooking into events. It is set up as an event emitter. You can register subscribers with the event emitter in order to react to events. The supported events are:

- `PRE_CREATE`
- `POST_CREATE`
- `PRE_ENABLE`
- `POST_ENABLE`
- `PRE_DISABLE`
- `POST_DISABLE`
- `PRE_DESTROY`
- `POST_DESTROY`
- `PRE_ADD_CONDITION`
- `POST_ADD_CONDITION`
- `PRE_SET_CONDITIONS`
- `POST_SET_CONDITIONS`
- `PRE_SET_CLIENT_DATA`
- `POST_SET_CLIENT_DATA`
- `PRE_SET_BUCKETER`
- `POST_SET_BUCKETER`

To register for these events, simply register listeners with the `events` property of `FeatureFlagClient` and use it like an [event emitter](https://pyee.readthedocs.io/en/latest/#pyee.BaseEventEmitter).

```python
from flipper import FeatureFlagClient, MemoryFeatureFlagStore
from flipper.events import EventType


def on_post_create(feature_name, is_enabled, client_data):
    print(feature_name, is_enabled, client_data)


client = FeatureFlagClient(MemoryFeatureFlagStore())
client.events.on(EventType.POST_CREATE, f=on_post_create)

client.create('HOMEPAGE_AB_TEST', is_enabled=True, client_data={"creator": "adambom"})
# > HOMEPAGE_AB_TEST True {"creator": "adambom"}
```

The event emitter also works as a decorator:

```python
client.events.on(EventType.POST_CREATE)
def on_post_create(feature_name, is_enabled, client_data):
    print(feature_name, is_enabled, client_data)
```

You can substitute your own event emitter for the default by setting the events property. The custom event emitter must implement `flipper.events.IEventEmitter`.

```python
client.events = MyCustomEventEmitter()
```

For the full usage of `FlipperEventEmitter` see the [pyee documentation](https://pyee.readthedocs.io/en/latest/#pyee.BaseEventEmitter).

## Subscribers

Flipper also exposes a `FlipperEventSubscriber` interface. It allows you to implement a method for each event type. You can then register this subscriber with the event emitter and it will call the appropriate methods. The event emitter exposes the methods `register_subscriber` and `remove_subscriber` for this purpose. For example:

```python
import logging

from flipper import FeatureFlagClient, MemoryFeatureFlagStore
from flipper.events import FlipperEventSubscriber


class LoggingEventSubscriber(FlipperEventSubscriber):
    def __init__(self, logger):
        self._logger = logger

    def on_post_create(self, feature_name, is_enabled, client_data):
        self._logger.info("flipper.create", extra={
            "feature_name": feature_name,
            "is_enabled": is_enabled,
            "client_data": client_data,
        })

    def on_post_enable(self, feature_name):
        self._logger.info("flipper.enable", extra={"feature_name": feature_name})

    def on_post_disable(self, feature_name):
        self._logger.info("flipper.disable", extra={"feature_name": feature_name})

    def on_post_destroy(self, feature_name):
        self._logger.info("flipper.destroy", extra={"feature_name": feature_name})

    def on_post_add_condition(self, feature_name, condition):
        self._logger.info("flipper.add_condition", extra={
            "feature_name": feature_name,
            "condition": condition.to_dict(),
        })

    def on_post_set_client_data(self, feature_name, client_data):
        self._logger.info("flipper.set_client_data", extra={
            "feature_name": feature_name,
            "client_data": client_data,
        })

    def on_post_set_bucketer(self, feature_name, bucketer):
        self._logger.info("flipper.set_bucketer", extra={
            "feature_name": feature_name,
            "bucketer": bucketer.to_dict(),
        })


logger = logging.getLogger("application")

client = FeatureFlagClient(MemoryFeatureFlagStore())
client.events.register_subscriber(LoggingEventSubscriber(logger))
```

# Development

Clone the repo and run `make install-dev` to get the environment set up. Test are run with the `pytest` command.


## Building thrift files

First, [install the thrift compiler](https://thrift.apache.org/tutorial/). On mac, the easiest way is to use homebrew:

```
brew install thrift
```

Then simply run `make thrift`. Remember to commit the results of the compilation step.

# System requirements

This project requires python version 3 or greater.

# Open Source

This library is made availble as open source under the Apache 2.0 license. This is not an officially supported Carta product.

## Development status

This project is actively maintained by the maintainers listed in the MAINTAINERS file. There are no major items on the project roadmap at this time, however bug fixes and new features may be added from time to time. We are open to contributions from the community as well.

## Contacts

The project maintainers can be reached via email at adam.savitzky@carta.com or luis.montiel@carta.com.

## Discussion

We use github issues for discussing features, bugs, and other project related issues.
