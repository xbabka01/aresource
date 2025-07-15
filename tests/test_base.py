import contextlib
from collections.abc import AsyncIterator

import pytest

from aresource.manager import BaseResource, ResourceManager


@pytest.mark.asyncio
async def test_simple_resource_manager() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""

    class ExampleResource(BaseResource[int]):
        """Example resource that yields the integer 42 when acquired."""

        @contextlib.asynccontextmanager
        async def acquire(self, manager: "ResourceManager") -> AsyncIterator[int]:
            """Asynchronously acquire the resource and yield 42."""
            yield 42

    class TestResourceManager(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test = ExampleResource()

    async with TestResourceManager() as manager:
        assert manager.test == 42
