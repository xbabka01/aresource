from collections.abc import AsyncGenerator, AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from aresource.base import BaseResource, ResourceManager


class CallbackResource[V, M: ResourceManager = ResourceManager](BaseResource[V, M]):
    def __init__(self, callback: Callable[[M], AbstractAsyncContextManager[V]]) -> None:
        self.callback = callback

    def acquire(self, manager: M) -> AbstractAsyncContextManager[V]:
        res = self.callback(manager)
        return res


def callback_resource[V, M: ResourceManager = ResourceManager](
    callback: Callable[[M], AbstractAsyncContextManager[V]],
) -> CallbackResource[V, M]:
    """A decorator to create a CallbackResource from a function."""
    return CallbackResource[V, M](callback)


def callback_context_resource[V, M: ResourceManager = ResourceManager](
    callback: Callable[[M], AsyncGenerator[V] | AsyncIterator[V]],
) -> CallbackResource[V, M]:
    """A decorator to create a CallbackResource from a function."""
    return CallbackResource[V, M](asynccontextmanager(callback))
