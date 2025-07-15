from aresource.manager import ResourceManager
from aresource.resources.files import (
    BytesResource,
)


async def test_bytes() -> None:
    class TestResourceManager(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test = BytesResource("aresource", "__init__.py")

    async with TestResourceManager() as manager:
        assert isinstance(manager.test, bytes)
        assert b"__all__" in manager.test
