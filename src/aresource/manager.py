import copy
import sys
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager
from typing import Any, ClassVar, Generic, Self, final

if sys.version_info <= (3, 11):
    from typing_extensions import TypeVar
else:
    from typing import TypeVar


T = TypeVar("T")
M = TypeVar("M", bound="ResourceManager", default="ResourceManager")


class BaseResource(ABC, Generic[T, M]):
    name: str | None = None

    @final
    def __get__(self, instance: "ResourceManager", owner: "type[ResourceManager]") -> T:
        return instance.get_resource(self.name)  # type: ignore[no-any-return]

    @final
    def __set_name__(self, owner: "type[ResourceManager]", name: str) -> None:
        owner.register_resource(name, self)

    @abstractmethod
    def acquire(self, manager: "M") -> AbstractAsyncContextManager[T]:
        """Acquire the resource asynchronously."""
        raise NotImplementedError("Must be implemented in a subclass")


class Resource(BaseResource[T, M], Generic[T, M]):
    def __init__(
        self,
        context: Callable[[Any], AbstractAsyncContextManager[T] | AsyncIterator[T]],
    ) -> None:
        self.context = context

    def acquire(self, manager: "M") -> AbstractAsyncContextManager[T]:
        res = self.context(manager)
        if isinstance(res, AbstractAsyncContextManager):
            return res
        elif isinstance(res, AsyncIterator):

            @asynccontextmanager
            def wrap() -> AsyncIterator[T]:
                return res

            return wrap()
        else:
            raise TypeError(
                f"{res.__name__} is not a subclass of AbstractAsyncContextManager|AsyncIterator"
            )


class ValueNotInitialized:
    pass


class ResourceManager:
    _cls: Any = None
    _resources: ClassVar[dict[str, BaseResource[Any]]] = {}

    def __init__(self) -> None:
        self._values: dict[str, Any] = dict.fromkeys(self._resources, ValueNotInitialized)
        self._exit_stack: AsyncExitStack | None = None

    @final
    @classmethod
    def register_resource(cls, name: str, resource: BaseResource[Any, Any]) -> None:
        """Register a resource with the manager."""
        if not isinstance(resource, BaseResource):
            raise TypeError(f"{resource.__name__} is not a subclass of BaseResource")
        if name in cls._resources:
            raise ValueError(f"Resource {name} is already registered in {cls.__name__}")
        # Create a copy of the class resources to avoid modifying the superclass
        if cls._cls is not cls:
            cls._resources = copy.deepcopy(cls._resources)
            cls._cls = cls

        cls._resources[name] = resource
        resource.name = name

    @final
    def get_resource(self, name: str | None) -> Any:
        """
        Get the value of a registered resource by name.
        """
        if name not in self._resources:
            raise AttributeError(f"Resource {name} is not registered in {self.__class__.__name__}")
        value = self._values[name]
        if value is ValueNotInitialized:
            raise AttributeError(
                f"Resource {name} is not initialized in {self.__class__.__name__}"
            )
        return value

    @final
    def set_resource(self, name: str, value: Any) -> None:
        """
        Set the value of a registered resource by name.
        Raises AttributeError if the resource is not registered.
        """
        if name not in self._resources:
            raise AttributeError(f"Resource {name} is not registered in {self.__class__.__name__}")
        self._values[name] = value

    async def setup(self) -> None:
        await self.__aenter__()

    async def __aenter__(self) -> Self:
        """Asynchronously enter the resource manager context, acquiring all resources.
        Each resource is acquired using its async context manager and set in the manager.
        Returns self.
        """
        if self._exit_stack is not None:
            raise RuntimeError("ResourceManager is already set up")

        self._exit_stack = AsyncExitStack()
        try:
            for name, handler in self._resources.items():
                value = await self._exit_stack.enter_async_context(handler.acquire(self))
                self.set_resource(name, value)
        except BaseException as exc:
            suppress = await self.__aexit__(type(exc), exc, exc.__traceback__)
            if not suppress:
                raise

        return self

    async def aclose(self) -> None:
        """Asynchronously close the resource manager, releasing all resources."""
        await self.__aexit__()

    async def __aexit__(self, *exc: Any) -> bool | None:
        """Asynchronously exit the resource manager context, releasing all resources.
        Delegates to the AsyncExitStack's __aexit__ method.
        Returns the result of the exit stack's __aexit__.
        """
        res: bool | None = False
        if self._exit_stack is not None:
            res = await self._exit_stack.__aexit__(*exc)
        self._exit_stack = None
        return res
