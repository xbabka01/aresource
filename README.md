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

Example of usage. Load config and use it to inicialize new session

```python
import asyncio

from aresource import ResourceManager
from aresource.aiohttp import ClientSessionResource
from aresource.files import HoconResource

class Manager(ResourceManager):
  data = HoconResource("tests", "config.conf")
  session = ClientSessionResource(lambda m: m.data['session'])

async def main() -> None:
  async with (
    Manager() as mng,
    mng.session.get('http://example.com') as resp
  ):
    print(await resp.read())

if __name__ == "__main__":
  asyncio.run(main())
```

## Examples

### Load data from package 

#### Load bytes from a Python file

```python
from aresource import ResourceManager
from aresource.files import BytesResource

class Manager(ResourceManager):
  data = BytesResource("aresource", "__init__.py")
```

#### Load HOCON configuration

```python
from aresource import ResourceManager
from aresource.files import HoconResource

class Manager(ResourceManager):
  data = HoconResource("tests", "data/test.conf")
```

**Note**: require optional dependency `pyhocon`

#### Load INI configuration

```python
from aresource import ResourceManager
from aresource.files import IniResource

class Manager(ResourceManager):
  data = IniResource("tests", "data/test.ini")
```

#### Load JSON data

```python
from aresource import ResourceManager
from aresource.files import JsonResource

class Manager(ResourceManager):
  data = JsonResource("tests", "data/test.json")
```

#### Load file path as a resource

```python
from aresource import ResourceManager
from aresource.files import PathResource

class Manager(ResourceManager):
  data = PathResource("tests", "data/test.json")
```

#### Load YAML data

```python
from aresource import ResourceManager
from aresource.files import YamlResource

class Manager(ResourceManager):
  data = YamlResource("tests", "data/test.yaml")
```

**Note**: require optional dependency `pyyaml`

### Aiohttp

**Note**: require optional dependency `aiohttp`

#### Create session


```python
from aresource import ResourceManager
from aresource.aiohttp import ClientSessionResource

class Manager(ResourceManager):
  data = ClientSessionResource()
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