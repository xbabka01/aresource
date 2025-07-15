import contextlib
from collections.abc import AsyncIterator

import pytest

from aresource.manager import BaseResource, ResourceManager


class ExampleResource(BaseResource[int]):
    """Example resource that yields the integer 42 when acquired."""

    def __init__(self, value: int = 42):
        self.value = value

    @contextlib.asynccontextmanager
    async def acquire(self, manager: "ResourceManager") -> AsyncIterator[int]:
        """Asynchronously acquire the resource and yield 42."""
        yield self.value


@pytest.mark.asyncio
async def test_simple_resource_manager() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""

    class TestResourceManager(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test = ExampleResource(42)

    async with TestResourceManager() as manager:
        assert manager.test == 42


@pytest.mark.asyncio
async def test_multiple_resource_manager() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""

    class Test1(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test1 = ExampleResource(0)

    class Test2(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test1 = ExampleResource(1)
        test2 = ExampleResource(2)

    async with Test1() as t1, Test2() as t2:
        assert t1.test1 == 0
        with pytest.raises(AttributeError):
            _ = t1.test2  # type: ignore

        assert t2.test1 == 1
        assert t2.test2 == 2


@pytest.mark.asyncio
async def test_inheritance_resource_manager() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""

    class Test1(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        test1 = ExampleResource(1)

    class Test2(Test1):
        """Resource manager containing the ExampleResource for testing."""

        test2 = ExampleResource(2)

    async with Test1() as t1, Test2() as t2:
        assert t1.test1 == 1
        with pytest.raises(AttributeError):
            _ = t1.test2  # type: ignore

        assert t2.test1 == 1
        assert t2.test2 == 2
