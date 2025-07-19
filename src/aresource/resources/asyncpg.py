import contextlib
from collections.abc import AsyncIterator, Callable
from typing import Any

import asyncpg # type: ignore[import-untyped]

from aresource.manager import BaseResource, ResourceManager


class AsyncPgConnectionResource(BaseResource[asyncpg.Connection]):
    """
    Resource that provides an aiohttp ClientSession.
    """

    def __init__(
        self, callback: Callable[[ResourceManager], dict[str, Any]] | None = None
    ) -> None:
        super().__init__()
        self.callback = callback

    @contextlib.asynccontextmanager
    async def acquire(self, manager: "ResourceManager") -> AsyncIterator[asyncpg.Connection]:
        kwargs = self.callback(manager) if self.callback else {}
        conn = await asyncpg.connect(**kwargs)
        try:
            yield conn
        finally:
            await conn.close()


class AsyncPgConnectionPoolResource(BaseResource[asyncpg.Pool]):
    """
    Resource that provides an aiohttp ClientSession.
    """

    def __init__(
        self, callback: Callable[[ResourceManager], dict[str, Any]] | None = None
    ) -> None:
        super().__init__()
        self.callback = callback

    @contextlib.asynccontextmanager
    async def acquire(self, manager: "ResourceManager") -> AsyncIterator[asyncpg.Pool]:
        kwargs = self.callback(manager) if self.callback else {}
        pool = await asyncpg.create_pool(**kwargs)
        try:
            yield pool
        finally:
            await pool.close()
