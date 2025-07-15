from aiohttp import web

from aresource.manager import ResourceManager
from aresource.resources.aiohttp.session import ClientSessionResource
from aresource.resources.aiohttp.web import WebAppResource


async def test_aiohttp() -> None:
    routes = web.RouteTableDef()

    @routes.get("/")
    async def hello(request: web.Request) -> web.Response:
        return web.Response(text="Hello, world")

    class TestResourceManager(ResourceManager):
        """Resource manager containing the ExampleResource for testing."""

        web = WebAppResource(routes=lambda _: routes)

        session = ClientSessionResource()

    async with (
        TestResourceManager() as manager,
        manager.session.get("http://localhost:8081/") as response,
    ):
        content = await response.read()
        assert content == b"Hello, world"
