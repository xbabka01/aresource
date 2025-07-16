import json

from aresource.manager import ResourceManager
from aresource.resources.files import BytesResource, HoconResource, IniResource, JsonResource
from aresource.resources.files.path import PathResource
from aresource.resources.files.yaml import YamlResource


async def test_bytes() -> None:
    class TestResourceManager(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test = BytesResource("aresource", "__init__.py")

    async with TestResourceManager() as manager:
        assert isinstance(manager.test, bytes)
        assert b"__all__" in manager.test


async def test_hocon() -> None:
    class TestResourceManager(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test = HoconResource("tests", "data/test.conf")

    async with TestResourceManager() as manager:
        assert manager.test == {"key": "value"}


async def test_ini() -> None:
    class TestResourceManager(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test = IniResource("tests", "data/test.ini")

    async with TestResourceManager() as manager:
        assert manager.test.sections() == ["forge.example"]


async def test_json() -> None:
    class TestResourceManager(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test = JsonResource("tests", "data/test.json")

    async with TestResourceManager() as manager:
        assert manager.test == {"key": "value"}


async def test_path() -> None:
    class TestResourceManager(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test = PathResource("tests", "data/test.json")

    async with TestResourceManager() as manager:
        assert manager.test.exists()
        data = json.loads(manager.test.read_text())
        assert data == {"key": "value"}


async def test_yaml() -> None:
    class TestResourceManager(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test = YamlResource("tests", "data/test.yaml")

    async with TestResourceManager() as manager:
        assert manager.test == [{"test": "test"}]
