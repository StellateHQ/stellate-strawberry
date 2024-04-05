import json
import queue
import requests
import threading
import time
import typing

from strawberry.extensions import SchemaExtension

def create_blake3_hash(input: str) -> int:
    val = 0

    if len(input) == 0:
        return val

    for char in input:
        code = ord(char)
        val = (val << 5) - val + code
        val &= 0xffffffff # Int32

    return val >> 0 # uInt32

def create_stellate_extension(service_name: str, token: str) -> SchemaExtension:
    class LoggingThread(threading.Thread):
        def __init__(self, queue, kwargs=None):
            threading.Thread.__init__(self, args=(), kwargs=None)
            self.queue = queue
            self.daemon = True

        def run(self):
            while True:
                payload = self.queue.get()
                self.log_to_stellate(payload)

        def log_to_stellate(self, payload):
            res = requests.post(
                f"https://{service_name}.stellate.sh/log",
                data=json.dumps(payload),
                headers={"stellate-logging-token": token, "content-type": "application/json"}
            )
            if res.status_code >= 300:
                print(f"Failed to log metrics to Stellate: {res.text[:100]}")

    q = queue.Queue()
    t = LoggingThread(q)
    t.start()

    class StellateMetricsLogging(SchemaExtension):
        def on_execute(self):
            start = time.time()
            yield
            end = time.time()

            result_json = json.dumps(self.get_result_dict(), indent=4)

            request = self.execution_context.context["request"] if self.execution_context.context else None
            response = self.execution_context.context["response"] if self.execution_context.context else None

            forwarded_for = request.headers.get('x-forwarded-for') if request != None else None
            ips = forwarded_for.split(',') if forwarded_for != None and len(forwarded_for) > 0 else []

            graphql_client_name = request.headers.get('x-graphql-client-name') if request != None else None
            graphql_client_version = request.headers.get('x-graphql-client-version') if request != None else None

            payload = {
              "operation": self.execution_context.query,
              "method": self.execution_context.context["request"].method if self.execution_context.context else "POST",
              "responseSize": len(result_json),
              "responseHash": create_blake3_hash(result_json),
              "elapsed": round((end - start) * 1_000),
              "operationName": self.execution_context.provided_operation_name,
              "variablesHash": create_blake3_hash(json.dumps(self.execution_context.variables or {})),
              "ip": ips[0] if len(ips) > 0 else request.headers.get('true-client-ip') or request.headers.get('x-real-ip') if request != None else None,
              "graphqlClientName": graphql_client_name,
              "graphqlClientVersion": graphql_client_version,
              "errors": self.execution_context.result.errors,
              "statusCode": self.execution_context.context["response"].status_code or 200 if self.execution_context.context != None else 200,
              "userAgent": request.headers.get("user-agent") if request != None else None,
              "referer": request.headers.get("referer") if request != None else None,
              "hasSetCookie": "set-cookie" in response.headers.keys() if response != None else None,
            }
            t.queue.put(payload)

        def get_result_dict(self):
            result = self.execution_context.result
            map = {}
            if result.data != None:
                map["data"] = result.data
            if result.errors != None:
                map["errors"] = result.errors
            if result.extensions != None:
                map["extensions"] = result.extensions
            return map

    return StellateMetricsLogging

def sync_schema_to_stellate(schema, service_name: str, token: str):
    res = requests.post(
        f"https://{service_name}.stellate.sh/schema",
        data=json.dumps({ "schema": schema.introspect() }),
        headers={"stellate-schema-token": token, "content-type": "application/json"}
    )
    if res.status_code >= 300:
        print(f"Failed to sync schema to Stellate: {res.text[:100]}")
