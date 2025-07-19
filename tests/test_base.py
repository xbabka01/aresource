import contextlib
from collections.abc import AsyncIterator

import pytest

from aresource.manager import BaseResource, ResourceManager, resource


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


async def test_decorator_resource_manager() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""

    class Test1(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        @resource
        async def test1(self: "Test1") -> AsyncIterator[int]:
            yield 1

    async with Test1() as t1:
        assert t1.test1 == 1


async def test_cleanup_oder_manager() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""
    cleaned = []

    class Test1(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        @resource
        async def test1(self: "Test1") -> AsyncIterator[int]:
            try:
                yield 1
            finally:
                cleaned.append(1)

        @resource
        async def test2(self: "Test1") -> AsyncIterator[int]:
            try:
                yield 2
            finally:
                cleaned.append(2)

        @resource
        async def test3(self: "Test1") -> AsyncIterator[int]:
            try:
                yield 3
            finally:
                cleaned.append(3)

    async with Test1() as t1:
        assert t1.test1 == 1
        assert t1.test2 == 2
        assert t1.test3 == 3

    assert cleaned == [3, 2, 1], "Resources should be cleaned up in reverse order of acquisition"


async def test_failure_cleanup_manager() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""
    cleaned = []

    class Test1(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        @resource
        async def test1(self: "Test1") -> AsyncIterator[int]:
            try:
                yield 1
            finally:
                cleaned.append(1)

        @resource
        async def test2(self: "Test1") -> AsyncIterator[int]:
            try:
                yield 2
            finally:
                cleaned.append(2)

        @resource
        async def test3(self: "Test1") -> AsyncIterator[int]:
            raise RuntimeError("This is a test failure")
            # This line will never be reached, but is needed for type checking
            yield None  # type: ignore[unreachable]

        @resource
        async def test4(self: "Test1") -> AsyncIterator[int]:
            try:
                yield 4
            finally:
                cleaned.append(4)

    with pytest.raises(RuntimeError):
        async with Test1():
            pytest.fail("This should not be reached")

    assert cleaned == [2, 1], "Resources should be cleaned up in reverse order of acquisition"


async def test_transitive_manager() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""
    cleaned = []

    class Test1(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        @resource
        async def test1(self: "Test1") -> AsyncIterator[int]:
            try:
                yield 1
            finally:
                cleaned.append(1)

        @resource
        async def test2(self: "Test1") -> AsyncIterator[int]:
            try:
                yield self.test1 + 1
            finally:
                cleaned.append(2)

    async with Test1() as t1:
        assert t1.test1 == 1
        assert t1.test2 == 2

    assert cleaned == [2, 1], "Resources should be cleaned up in reverse order of acquisition"


def test_fail() -> None:
    pytest.fail("This is a test failure that should not be caught by the ResourceManager")
