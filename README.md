# aresource

[![pypi](https://img.shields.io/pypi/v/aresource)](https://pypi.org/project/aresource/)
[![python](https://img.shields.io/pypi/pyversions/aresource.svg)](https://pypi.org/project/aresource/)

A Python project for resource management.

## Project Structure

```
src/
  aresource/
tests/
```

## Installation

Use pip to install released version:

```sh
pip install aresource
```

Use [Poetry](https://python-poetry.org/) to install local version:

```sh
poetry install
```

## Usage



```python
from aresource import ResourceManager, resource
from aresource.aiohttp.session import ClientSessionResource
from typing import AsyncIterator

...

class Test(ResourceManager):
  session = ClientSessionResource()

  @resource
  async def data(self: "Test") -> AsyncIterator[str]:
    async with self.session.get('https://example.com') as resp:
      data = await resp.read()
    yield data

...

async with Test() as mng:
  print(msg.data)
```

## Testing

Run tests with:

```sh
poetry run pytest
```

## Code Quality

Command to format and lint code:

```sh
poetry run ruff format .
poetry run ruff check --fix
poetry run mypy .

```

## License

MIT License