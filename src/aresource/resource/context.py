from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from aresource.base import BaseResource, ResourceManager


class ContextResource[V, M: ResourceManager = ResourceManager](BaseResource[V, M]):
    def __init__(
        self,
        context: AbstractAsyncContextManager[V],
    ) -> None:
        self.context = context

    @asynccontextmanager
    async def acquire(self, manager: M) -> AsyncIterator[V]:
        async with self.context as val:
            yield val
