# aresource

[![pypi](https://img.shields.io/pypi/v/aresource)](https://pypi.org/project/aresource/)
[![python](https://img.shields.io/pypi/pyversions/aresource.svg)](https://pypi.org/project/aresource/)
[![Tests](https://github.com/xbabka01/aresource/actions/workflows/python.yml/badge.svg)](https://github.com/xbabka01/aresource/actions/workflows/python.yml)

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

Example of usage. Load config and use it to initialize new session

```python
import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from io import TextIOBase

from aresource import callback_context_resource, ResourceManager


class Manager(ResourceManager):
    @callback_context_resource
    async def file(self) -> AsyncIterator[TextIOBase]:
        with open("config.txt", "w") as f:
            yield f


async def main() -> None:
    async with Manager() as mng:
        mng.file.write("Hello, World!")


if __name__ == "__main__":
    asyncio.run(main())
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
