from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from aresource.base import BaseResource, ResourceManager


class CallbackResource[V, M: ResourceManager = ResourceManager](BaseResource[V, M]):
    def __init__(
        self,
        context: Callable[[M], AbstractAsyncContextManager[V]],
    ) -> None:
        self.context = context

    def acquire(self, manager: M) -> AbstractAsyncContextManager[V]:
        return self.context(manager)
