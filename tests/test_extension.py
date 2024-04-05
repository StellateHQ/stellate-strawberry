import strawberry

from stellate_strawberry import create_stellate_extension


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "world"

    @strawberry.field
    def fails(self) -> str | None:
        raise ValueError("This is an error")


def test_extension_happy_path(mocker):
    queue_mock = mocker.patch("queue.Queue.put")

    extension = create_stellate_extension("service_name", "token")
    schema = strawberry.Schema(query=Query, extensions=[extension])

    schema.execute_sync("{ hello }")

    assert queue_mock.call_count == 1

    call_args = queue_mock.call_args[0][0]

    assert call_args["operation"] == "{ hello }"
    assert call_args["method"] == "POST"
    assert call_args["responseSize"] == 48
    assert call_args["operationName"] is None
    assert call_args["variablesHash"] == 3938
    assert call_args["ip"] is None
    assert call_args["graphqlClientName"] is None
    assert call_args["graphqlClientVersion"] is None
    assert call_args["errors"] is None
    assert call_args["statusCode"] == 200
    assert call_args["userAgent"] is None
    assert call_args["referer"] is None
    assert call_args["hasSetCookie"] is None


def test_extension_errors(mocker):
    queue_mock = mocker.patch("queue.Queue.put")

    extension = create_stellate_extension("service_name", "token")
    schema = strawberry.Schema(query=Query, extensions=[extension])

    schema.execute_sync("{ fails }")

    assert queue_mock.call_count == 1

    call_args = queue_mock.call_args[0][0]

    assert call_args["operation"] == "{ fails }"
    assert call_args["method"] == "POST"
    assert call_args["responseSize"] == 332
    assert call_args["operationName"] is None
    assert call_args["variablesHash"] == 3938
    assert call_args["ip"] is None
    assert call_args["graphqlClientName"] is None
    assert call_args["graphqlClientVersion"] is None
    assert call_args["errors"] == [
        {
            "locations": [{"column": 3, "line": 1}],
            "message": "This is an error",
            "path": ["fails"],
        }
    ]
    assert call_args["statusCode"] == 200
    assert call_args["userAgent"] is None
    assert call_args["referer"] is None
    assert call_args["hasSetCookie"] is None
