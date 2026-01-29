<div id="toc" align="center" style="margin-bottom: 0;">
  <ul style="list-style: none; margin: 0; padding: 0;">
    <a href="https://stagehand.dev">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/browserbase/stagehand/main/media/dark_logo.png" />
        <img alt="Stagehand" src="https://raw.githubusercontent.com/browserbase/stagehand/main/media/light_logo.png" width="200" style="margin-right: 30px;" />
      </picture>
    </a>
  </ul>
</div>
<p align="center">
  <strong>The AI Browser Automation Framework</strong><br>
  <a href="https://docs.stagehand.dev/v3/sdk/python">Read the Docs</a>
</p>

<p align="center">
  <a href="https://github.com/browserbase/stagehand/tree/main?tab=MIT-1-ov-file#MIT-1-ov-file">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/browserbase/stagehand/main/media/dark_license.svg" />
      <img alt="MIT License" src="https://raw.githubusercontent.com/browserbase/stagehand/main/media/light_license.svg" />
    </picture>
  </a>
  <a href="https://stagehand.dev/discord">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/browserbase/stagehand/main/media/dark_discord.svg" />
      <img alt="Discord Community" src="https://raw.githubusercontent.com/browserbase/stagehand/main/media/light_discord.svg" />
    </picture>
  </a>
</p>
<!-- prettier-ignore -->
[![PyPI version](https://img.shields.io/pypi/v/stagehand.svg?label=pypi%20(stable))](https://pypi.org/project/stagehand/)

<p align="center">
	<a href="https://trendshift.io/repositories/12122" target="_blank"><img src="https://trendshift.io/api/badge/repositories/12122" alt="browserbase%2Fstagehand | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

<p align="center">
If you're looking for other languages, you can find them
<a href="https://docs.stagehand.dev/v3/first-steps/introduction"> here</a>
</p>

<div align="center" style="display: flex; align-items: center; justify-content: center; gap: 4px; margin-bottom: 0;">
  <b>Vibe code</b>
  <span style="font-size: 1.05em;"> Stagehand with </span>
  <a href="https://director.ai" style="display: flex; align-items: center;">
    <span>Director</span>
  </a>
  <span> </span>
  <picture>
    <img alt="Director" src="https://raw.githubusercontent.com/browserbase/stagehand/main/media/director_icon.svg" width="25" />
  </picture>
</div>

> [!TIP]
> Migrating from the old v2 Python SDK? See our [migration guide here](https://docs.stagehand.dev/v3/migrations/python).

## What is Stagehand?

Stagehand is a browser automation framework used to control web browsers with natural language and code. By combining the power of AI with the precision of code, Stagehand makes web automation flexible, maintainable, and actually reliable.

## Why Stagehand?

Most existing browser automation tools either require you to write low-level code in a framework like Selenium, Playwright, or Puppeteer, or use high-level agents that can be unpredictable in production. By letting developers choose what to write in code vs. natural language (and bridging the gap between the two) Stagehand is the natural choice for browser automations in production.

1. **Choose when to write code vs. natural language**: use AI when you want to navigate unfamiliar pages, and use code when you know exactly what you want to do.

2. **Go from AI-driven to repeatable workflows**: Stagehand lets you preview AI actions before running them, and also helps you easily cache repeatable actions to save time and tokens.

3. **Write once, run forever**: Stagehand's auto-caching combined with self-healing remembers previous actions, runs without LLM inference, and knows when to involve AI whenever the website changes and your automation breaks.

## Installation

```sh
# install from PyPI
uv pip install stagehand
```

For local development or when working from this repository, sync the dependency lockfile with `uv` (see the Local development section below) before running project scripts.

## Requirements

Python 3.9 or higher.

## Running the Example

A complete working example is available at [`examples/full_example.py`](examples/full_example.py).

To run it, first export the required environment variables, then use Python:

```bash
export BROWSERBASE_API_KEY="your-bb-api-key"
export BROWSERBASE_PROJECT_ID="your-bb-project-uuid"
export MODEL_API_KEY="sk-proj-your-llm-api-key"

uv run python examples/full_example.py
```

## Local mode example

If you want to run Stagehand locally, use the local example (`examples/local_example.py`). It shows how to configure the client for `server="local"`.

Local mode runs Stagehand’s embedded server and launches a **local Chrome/Chromium** browser (it is **not bundled** with the Python wheel), so you must have Chrome installed on the machine running the example.

If Chrome is installed but Stagehand can’t find it, set `CHROME_PATH` to your browser executable (or pass `browser.launchOptions.executablePath` when starting the session).

Common Windows paths:
- `C:\Program Files\Google\Chrome\Application\chrome.exe`
- `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`

PowerShell:

```powershell
# optional if you don't already have Chrome installed
winget install -e --id Google.Chrome

# optional if Stagehand can't auto-detect Chrome
$env:CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"

uv run python examples/local_example.py
```

```bash
pip install stagehand
uv run python examples/local_example.py
```

## Streaming logging example

See [`examples/logging_example.py`](examples/logging_example.py) for a remote-only flow that streams `StreamEvent`s with `verbose=2`, `stream_response=True`, and `x_stream_response="true"` so you can watch the SDK’s logs as they arrive.

```bash
uv run python examples/logging_example.py
```

<details>
<summary><strong>Local development</strong></summary>

This repository relies on `uv` to install the sanctioned Python version and dependencies. After cloning, bootstrap the environment with:

```sh
./scripts/bootstrap
```
Once the environment is ready, execute repo scripts with `uv run`:

```sh
uv run python examples/full_example.py
```
</details>

## Usage

This example demonstrates the full Stagehand workflow: starting a session, navigating to a page, observing possible actions, acting on elements, extracting data, and running an autonomous agent.

```python
import asyncio

from stagehand import AsyncStagehand


async def main() -> None:
    # Create client using environment variables:
    # BROWSERBASE_API_KEY, BROWSERBASE_PROJECT_ID, MODEL_API_KEY
    client = AsyncStagehand()

    # Start a new browser session (returns a session helper bound to a session_id)
    session = await client.sessions.start(model_name="openai/gpt-5-nano")

    print(f"Session started: {session.id}")

    try:
        # Navigate to a webpage
        await session.navigate(
            url="https://news.ycombinator.com",
        )
        print("Navigated to Hacker News")

        # Observe to find possible actions on the page
        observe_response = await session.observe(
            instruction="find the link to view comments for the top post",
        )

        results = observe_response.data.result
        print(f"Found {len(results)} possible actions")
        if not results:
            return

        # Take the first action returned by Observe and pass it to Act
        action = results[0].to_dict(exclude_none=True)
        print("Acting on:", action.get("description"))

        act_response = await session.act(input=action)
        print("Act completed:", act_response.data.result.message)

        # Extract structured data from the page using a JSON schema
        extract_response = await session.extract(
            instruction="extract the text of the top comment on this page",
            schema={
                "type": "object",
                "properties": {
                    "commentText": {"type": "string"},
                    "author": {"type": "string"},
                },
                "required": ["commentText"],
            },
        )

        extracted = extract_response.data.result
        author = extracted.get("author", "unknown") if isinstance(extracted, dict) else "unknown"
        print("Extracted author:", author)

        # Run an autonomous agent to accomplish a complex task
        execute_response = await session.execute(
            execute_options={
                "instruction": f"Find any personal website, GitHub, or LinkedIn profile for the Hacker News user '{author}'.",
                "max_steps": 10,
            },
            agent_config={"model": "openai/gpt-5-nano"},
            timeout=300.0,
        )

        print("Agent completed:", execute_response.data.result.message)
        print("Agent success:", execute_response.data.result.success)
    finally:
        # End the browser session to clean up resources
        await session.end()
        print("Session ended")


if __name__ == "__main__":
    asyncio.run(main())
```

## Client configuration

Configure the client using environment variables:

```python
from stagehand import AsyncStagehand

client = AsyncStagehand()
```

Or manually:

```python
from stagehand import AsyncStagehand

client = AsyncStagehand(
    browserbase_api_key="My Browserbase API Key",
    browserbase_project_id="My Browserbase Project ID",
    model_api_key="My Model API Key",
)
```

Or using a combination of the two approaches:

```python
from stagehand import AsyncStagehand

client = AsyncStagehand(
    # Configures using environment variables
    browserbase_api_key="My Browserbase API Key",  # override just this one
)
```

See this table for the available options:

| Keyword argument         | Environment variable     | Required | Default value                             |
| ------------------------ | ------------------------ | -------- | ----------------------------------------- |
| `browserbase_api_key`    | `BROWSERBASE_API_KEY`    | true     | -                                         |
| `browserbase_project_id` | `BROWSERBASE_PROJECT_ID` | true     | -                                         |
| `model_api_key`          | `MODEL_API_KEY`          | true     | -                                         |
| `base_url`               | `STAGEHAND_BASE_URL`     | false    | `"https://api.stagehand.browserbase.com"` |

Keyword arguments take precedence over environment variables.

> [!TIP]
> Don't create more than one client in the same application. Each client has a connection pool, which is more efficient to share between requests.

### Modifying configuration

To temporarily use a modified client configuration while reusing the same connection pool, call `with_options()` on any client:

```python
client_with_options = client.with_options(model_api_key="sk-your-llm-api-key-here", max_retries=42)
```

The `with_options()` method does not affect the original client.

## Requests and responses

To send a request to the Stagehand API, call the corresponding client method using keyword arguments.

Nested request parameters are dictionaries typed using [`TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev) which also provide helper methods like:

- Serializing back into JSON: `model.to_json()`
- Converting to a dictionary: `model.to_dict()`

## Immutability

Response objects are Pydantic models. If you want to build a modified copy, prefer `model.model_copy(update={...})` (Pydantic v2) rather than mutating in place.

## Asynchronous execution

This SDK recommends using `AsyncStagehand` and `await`ing each API call:

```python
import asyncio
from stagehand import AsyncStagehand


async def main() -> None:
    client = AsyncStagehand()
    session = await client.sessions.start(model_name="openai/gpt-5-nano")
    response = await session.act(input="click the first link on the page")
    print(response.data)


asyncio.run(main())
```

### With aiohttp

By default, the async client uses `httpx` for HTTP requests. For improved concurrency performance you may also use `aiohttp` as the HTTP backend.

Install `aiohttp`:

```sh
# install from PyPI
uv pip install stagehand[aiohttp]
```

Then instantiate the client with `http_client=DefaultAioHttpClient()`:

```python
import asyncio
from stagehand import AsyncStagehand, DefaultAioHttpClient


async def main() -> None:
    async with AsyncStagehand(http_client=DefaultAioHttpClient()) as client:
        session = await client.sessions.start(model_name="openai/gpt-5-nano")
        response = await session.act(input="click the first link on the page")
        print(response.data)


asyncio.run(main())
```

## Streaming responses

We provide support for streaming responses using Server-Sent Events (SSE).

To enable SSE streaming, you must:

1. Ask the server to stream by setting `x_stream_response="true"` (header), and
2. Tell the client to parse an SSE stream by setting `stream_response=True`.

```python
import asyncio

from stagehand import AsyncStagehand


async def main() -> None:
    async with AsyncStagehand() as client:
        session = await client.sessions.start(model_name="openai/gpt-5-nano")

        stream = await client.sessions.act(
            id=session.id,
            input="click the first link on the page",
            stream_response=True,
            x_stream_response="true",
        )
        async for event in stream:
            # event is a StreamEvent (type: "system" | "log")
            print(event.type, event.data)


asyncio.run(main())
```

## Raw responses

The SDK defines methods that deserialize responses into Pydantic models. However, these methods don't provide access to response headers, status code, or the raw response body.

To access this data, prefix any HTTP method call on a client or service with `with_raw_response`:

```python
import asyncio

from stagehand import AsyncStagehand


async def main() -> None:
    async with AsyncStagehand() as client:
        response = await client.sessions.with_raw_response.start(model_name="openai/gpt-5-nano")
        print(response.headers.get("X-My-Header"))

        session = response.parse()  # get the object that `sessions.start()` would have returned
        print(session.data)


asyncio.run(main())
```

### `.with_streaming_response`

The `with_raw_response` interface eagerly reads the full response body when you make the request.

To stream the response body (not SSE), use `with_streaming_response` instead. It requires a context manager and only reads the response body once you call `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()` or `.parse()`.

```python
import asyncio

from stagehand import AsyncStagehand


async def main() -> None:
    async with AsyncStagehand() as client:
        async with client.sessions.with_streaming_response.start(model_name="openai/gpt-5-nano") as response:
            print(response.headers.get("X-My-Header"))
            async for line in response.iter_lines():
                print(line)


asyncio.run(main())
```

## Error handling

When the library is unable to connect to the API (for example, due to network connection problems or a timeout), a subclass of `stagehand.APIConnectionError` is raised.

When the API returns a non-success status code (that is, 4xx or 5xx response), a subclass of `stagehand.APIStatusError` is raised, containing `status_code` and `response` properties.

All errors inherit from `stagehand.APIError`.

```python
import asyncio

import stagehand
from stagehand import AsyncStagehand


async def main() -> None:
    async with AsyncStagehand() as client:
        try:
            await client.sessions.start(model_name="openai/gpt-5-nano")
        except stagehand.APIConnectionError as e:
            print("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        except stagehand.RateLimitError:
            print("A 429 status code was received; we should back off a bit.")
        except stagehand.APIStatusError as e:
            print("A non-200-range status code was received")
            print(e.status_code)
            print(e.response)


asyncio.run(main())
```

Error codes are as follows:

| Status Code | Error Type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 422         | `UnprocessableEntityError` |
| 429         | `RateLimitError`           |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |

### Retries

Certain errors are automatically retried 2 times by default, with a short exponential backoff. Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the `max_retries` option to configure or disable retry settings:

```python
import asyncio

from stagehand import AsyncStagehand


async def main() -> None:
    async with AsyncStagehand(max_retries=0) as client:
        # Or, configure per-request:
        await client.with_options(max_retries=5).sessions.start(model_name="openai/gpt-5-nano")


asyncio.run(main())
```

### Timeouts

By default requests time out after 1 minute. You can configure this with a `timeout` option, which accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/timeouts/#fine-tuning-the-configuration) object.

On timeout, an `APITimeoutError` is thrown. Note that requests that time out are [retried twice by default](#retries).

## Logging

The SDK uses the standard library [`logging`](https://docs.python.org/3/library/logging.html) module.

Enable logging by setting the `STAGEHAND_LOG` environment variable to `info`:

```sh
export STAGEHAND_LOG=info
```

Or to `debug` for more verbose logging:

```sh
export STAGEHAND_LOG=debug
```

## Undocumented API functionality

This library is typed for convenient access to the documented API, but you can still access undocumented endpoints, request params, or response properties when needed.

### Undocumented endpoints

To make requests to undocumented endpoints, use `client.get`, `client.post`, and other HTTP verbs. Client options (such as retries) are respected.

```python
import httpx
from stagehand import AsyncStagehand

import asyncio


async def main() -> None:
    async with AsyncStagehand() as client:
        response = await client.post("/foo", cast_to=httpx.Response, body={"my_param": True})
        print(response.headers.get("x-foo"))


asyncio.run(main())
```

### Undocumented request params

To send extra params that aren't available as keyword args, use `extra_query`, `extra_body`, and `extra_headers`.

### Undocumented response properties

To access undocumented response properties, you can access extra fields like `response.unknown_prop`. You can also get all extra fields as a dict with [`response.model_extra`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_extra).

## Response validation

In rare cases, the API may return a response that doesn't match the expected type.

By default, the SDK is permissive and will only raise an error if you later try to use the invalid data.

If you would prefer to validate responses upfront, instantiate the client with `_strict_response_validation=True`. An `APIResponseValidationError` will be raised if the API responds with invalid data for the expected schema.

```python
import asyncio

from stagehand import APIResponseValidationError, AsyncStagehand

try:
    async def main() -> None:
        async with AsyncStagehand(_strict_response_validation=True) as client:
            await client.sessions.start(model_name="openai/gpt-5-nano")

    asyncio.run(main())
except APIResponseValidationError as e:
    print("Response failed schema validation:", e)
```

## FAQ

### Why are some values typed as `Literal[...]` instead of Python `Enum`s?

Using `Literal[...]` types is forwards compatible: the API can introduce new enum values without breaking older SDKs at runtime.

### How can I tell whether `None` means `null` or “missing” in a response?

In an API response, a field may be explicitly `null`, or missing entirely; in either case its value is `None` in this library. You can differentiate the two cases with `.model_fields_set`:

```python
if response.my_field is None:
    if "my_field" not in response.model_fields_set:
        print('Got json like {}, without a "my_field" key present at all.')
    else:
        print('Got json like {"my_field": null}.')
```

### Accessing raw response data (e.g. headers)

The "raw" Response object can be accessed by prefixing `.with_raw_response.` to any HTTP method call, e.g.,

```py
from stagehand import Stagehand

client = Stagehand()
response = client.sessions.with_raw_response.start(
    model_name="openai/gpt-5-nano",
)
print(response.headers.get('X-My-Header'))

session = response.parse()  # get the object that `sessions.start()` would have returned
print(session.data)
```

These methods return an [`APIResponse`](https://github.com/browserbase/stagehand-python/tree/main/src/stagehand/_response.py) object.

The async client returns an [`AsyncAPIResponse`](https://github.com/browserbase/stagehand-python/tree/main/src/stagehand/_response.py) with the same structure, the only difference being `await`able methods for reading the response content.

#### `.with_streaming_response`

The above interface eagerly reads the full response body when you make the request, which may not always be what you want.

To stream the response body, use `.with_streaming_response` instead, which requires a context manager and only reads the response body once you call `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()` or `.parse()`. In the async client, these are async methods.

```python
with client.sessions.with_streaming_response.start(
    model_name="openai/gpt-5-nano",
) as response:
    print(response.headers.get("X-My-Header"))

    for line in response.iter_lines():
        print(line)
```

The context manager is required so that the response will reliably be closed.

### Making custom/undocumented requests

This library is typed for convenient access to the documented API.

If you need to access undocumented endpoints, params, or response properties, the library can still be used.

#### Undocumented endpoints

To make requests to undocumented endpoints, you can make requests using `client.get`, `client.post`, and other
http verbs. Options on the client will be respected (such as retries) when making this request.

```py
import httpx

response = client.post(
    "/foo",
    cast_to=httpx.Response,
    body={"my_param": True},
)

print(response.headers.get("x-foo"))
```

#### Undocumented request params

If you want to explicitly send an extra param, you can do so with the `extra_query`, `extra_body`, and `extra_headers` request
options.

#### Undocumented response properties

To access undocumented response properties, you can access the extra fields like `response.unknown_prop`. You
can also get all the extra fields on the Pydantic model as a dict with
[`response.model_extra`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_extra).

### Configuring the HTTP client

You can directly override the [httpx client](https://www.python-httpx.org/api/#client) to customize it for your use case, including:

- Support for [proxies](https://www.python-httpx.org/advanced/proxies/)
- Custom [transports](https://www.python-httpx.org/advanced/transports/)
- Additional [advanced](https://www.python-httpx.org/advanced/clients/) functionality

```python
import httpx
from stagehand import Stagehand, DefaultHttpxClient

client = Stagehand(
    # Or use the `STAGEHAND_BASE_URL` env var
    base_url="http://my.test.server.example.com:8083",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

You can also customize the client on a per-request basis by using `with_options()`:

```python
client.with_options(http_client=DefaultHttpxClient(...))
```

### Managing HTTP resources

By default the library closes underlying HTTP connections whenever the client is [garbage collected](https://docs.python.org/3/reference/datamodel.html#object.__del__). You can manually close the client using the `.close()` method if desired, or with a context manager that closes when exiting.

```py
from stagehand import Stagehand

with Stagehand() as client:
  # make requests here
  ...

# HTTP client is now closed
```

## Versioning

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals.)_
3. Changes that we do not expect to impact the vast majority of users in practice.

We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an [issue](https://www.github.com/browserbase/stagehand-python/issues) with questions, bugs, or suggestions.

### Determining the installed version

If you've upgraded to the latest version but aren't seeing any new features you were expecting then your python environment is likely still using an older version.

You can determine the version that is being used at runtime with:

```python
import stagehand

print(stagehand.__version__)
```
