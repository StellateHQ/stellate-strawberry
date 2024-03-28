# stellate-strawberry

This package integrates your Strawberry GraphQL API with Stellate. It does so by providing you with an [Extension](https://strawberry.rocks/docs/extensions) that you can add to your schema with one line of code.

## Installation

Simply install the package using `pip`:

```sh
pip install stellate-strawberry
```

## Set Up

Before you can make use of this library, you need to [set up a Stellate service](https://stellate.co/docs/quickstart#1-create-stellate-service) and [create a logging token](https://stellate.co/docs/graphql-metrics/metrics-get-started#create-your-own-logging-token).

After that, add the Stellate extension when initializing your `strawberry.Schema` object in order to add [Stellate Metrics Logging](https://stellate.co/docs/graphql-metrics/metrics-get-started#metrics-collection):

```py
from stellate_strawberry import create_stellate_extension

service_name = "my-service"  # The name of your Stellate service
token = "stl8_xyz"           # The logging token for above service

schema = strawberry.Schema(
    query=Query,
    extensions=[create_stellate_extension(service_name, token)]
)
```

Stellate GraphQL Metrics are even more powerful if Stellate knows about your GraphQL schema. Set up automatic schema synchronization like so:

```py
from stellate_strawberry import sync_schema_to_stellate

service_name = "my-service"  # The name of your Stellate service
token = "stl8_xyz"           # The logging token for above service

schema = strawberry.Schema(query=Query)
sync_schema_to_stellate(schema, service_name, token)
```
