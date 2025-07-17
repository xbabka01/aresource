# aresource

[![version]("https://img.shields.io/pypi/v/aresource?color=%2334D058&label=pypi%20package)](https://pypi.org/project/aresource/)
[![python]("https://img.shields.io/pypi/pyversions/aresource.svg?color=%2334D058)](https://pypi.org/project/aresource/)

A Python project for resource management.

## Project Structure

```
src/
  aresource/
tests/
```

## Installation

Use [Poetry](https://python-poetry.org/) to install dependencies:

```sh
poetry install
```

## Usage

Import and use the package in your Python code:

```python
from aresource import manager
```

## Testing

Run tests with:

```sh
poetry run pytest
```

## Code Quality

- Type checking: `poetry run mypy src/`
- Linting: `poetry run ruff src/`

## License

MIT License