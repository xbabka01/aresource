import contextlib
from collections.abc import AsyncIterator, Callable
from typing import Any

import pytest

from aresource import (
    BaseResource,
    ResourceManager,
    callback_context_resource,
    callback_resource,
    context_resource,
)


class IntResource(BaseResource[int, ResourceManager]):
    def __init__(
        self,
        value: int,
        on_call: Callable[[int], None] | None = None,
        on_cleanup: Callable[[int], None] | None = None,
    ) -> None:
        self.value = value
        self.on_call = on_call
        self.on_cleanup = on_cleanup

    @contextlib.asynccontextmanager
    async def acquire(self, manager: ResourceManager) -> AsyncIterator[int]:
        """Asynchronously acquire the resource and yield 42."""
        try:
            if self.on_call is not None:
                self.on_call(self.value)
            yield self.value
        finally:
            if self.on_cleanup:
                self.on_cleanup(self.value)


def raise_value_error(*args: Any, **kwargs: Any) -> None:
    raise ValueError("Expected a ValueError")


async def test_single() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""

    class M(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        value = IntResource(42)

    async with M() as manager:
        assert manager.value == 42


async def test_multiple() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""

    class M1(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        t1 = IntResource(0)

    class M2(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        t1 = IntResource(1)
        t2 = IntResource(2)

    async with M1() as m1, M2() as m2:
        assert m1.t1 == 0
        with pytest.raises(AttributeError):
            _ = m1.t2  # type: ignore

        assert m2.t1 == 1
        assert m2.t2 == 2


async def test_inheritance() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""

    class M1(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        t1 = IntResource(1)

    class M2(M1):
        """Resource manager containing the ExampleResource for testing."""

        t2 = IntResource(2)

    async with M1() as m1, M2() as m2:
        assert m1.t1 == 1
        with pytest.raises(AttributeError):
            _ = m1.t2  # type: ignore[attr-defined]

        assert m2.t1 == 1
        assert m2.t2 == 2


async def test_decorator() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""

    class M1(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        @callback_context_resource
        async def t1(self) -> AsyncIterator[int]:
            yield 1

    async with M1() as m1:
        assert m1.t1 == 1


async def test_cleanup_oder() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""
    cleaned: list[int] = []

    class M(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        t1 = IntResource(1, on_cleanup=cleaned.append)
        t2 = IntResource(2, on_cleanup=cleaned.append)
        t3 = IntResource(3, on_cleanup=cleaned.append)

    async with M() as m:
        assert m.t1 == 1
        assert m.t2 == 2
        assert m.t3 == 3

    assert cleaned == [3, 2, 1], "Resources should be cleaned up in reverse order of acquisition"


async def test_failure_setup() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""
    cleaned: list[int] = []

    class M(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        t1 = IntResource(1, on_cleanup=cleaned.append)
        t2 = IntResource(2, on_cleanup=cleaned.append)
        t3 = IntResource(3, on_call=raise_value_error)

        # This should not be reached as setup will fail on t3
        t4 = IntResource(4, on_cleanup=cleaned.append)

    with pytest.raises(ValueError):
        async with M():
            pytest.fail("This should not be reached")

    assert cleaned == [2, 1], "Resources should be cleaned up in reverse order of acquisition"


async def test_failure_cleanup() -> None:
    cleaned: list[int] = []

    class M(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        t1 = IntResource(1, on_cleanup=cleaned.append)
        t2 = IntResource(2, on_cleanup=cleaned.append)
        t3 = IntResource(2, on_cleanup=raise_value_error)
        t4 = IntResource(4, on_cleanup=cleaned.append)

    with pytest.raises(ValueError):
        async with M():
            pytest.fail("This should not be reached")

    assert cleaned == [4, 2, 1], "Resources should be cleaned up in reverse order of acquisition"


async def test_transitive() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""
    cleaned: list[int] = []

    class M(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        @callback_context_resource
        async def t1(self) -> AsyncIterator[int]:
            try:
                yield 1
            finally:
                cleaned.append(1)

        @callback_context_resource
        async def t2(self) -> AsyncIterator[int]:
            try:
                yield self.t1 + 1
            finally:
                cleaned.append(2)

    async with M() as m:
        assert m.t1 == 1
        assert m.t2 == 2

    assert cleaned == [2, 1], "Resources should be cleaned up in reverse order of acquisition"


async def test_wrong_order() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""
    cleaned: list[int] = []

    class M(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        @callback_context_resource
        async def t2(self) -> AsyncIterator[int]:
            try:
                yield self.t1 + 1
            finally:
                cleaned.append(2)

        @callback_context_resource
        async def t1(self) -> AsyncIterator[int]:
            try:
                yield 1
            finally:
                cleaned.append(1)

    with pytest.raises(AttributeError):
        async with M():
            pytest.fail("This should not be reached")
    assert cleaned == [2], "Resources should be cleaned up in reverse order of acquisition"


async def test_with_callback_manager() -> None:
    """Test that ResourceManager can acquire and return a simple ExampleResource asynchronously."""

    @contextlib.asynccontextmanager
    async def context(_: ResourceManager) -> AsyncIterator[int]:
        yield 1

    class A(ResourceManager):
        val = callback_resource(context)

    async with A() as a:
        assert a.val == 1


async def test_with_context_manager() -> None:
    @contextlib.asynccontextmanager
    async def x() -> AsyncIterator[int]:
        yield 1

    class B(ResourceManager):
        val = context_resource(x())

    async with B() as b:
        assert b.val == 1
