import copy
from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, AsyncExitStack
from typing import Any, ClassVar, Final, Self, final, overload


class BaseResource[V, M: ResourceManager = ResourceManager](ABC):
    name: str | None = None

    @overload
    def __get__(self, manager: None, owner: type[M]) -> Self:
        pass

    @overload
    def __get__(self, manager: M, owner: type[M]) -> V:
        pass

    def __get__(self, manager: M | None, owner: type[M]) -> Self | V:
        if manager is None:
            return self
        return manager.get_resource(self.name)  # type: ignore[no-any-return]

    def __set_name__(self, owner: type[M], name: str) -> None:
        owner.register_resource(name, self)

    @abstractmethod
    def acquire(self, manager: M) -> AbstractAsyncContextManager[V]:
        """Acquire the resource asynchronously."""
        raise NotImplementedError("Must be implemented in a subclass")


class ValueNotInitialized:
    pass


class ResourceManager:
    _cls: Any = None
    _resources: ClassVar[dict[str, BaseResource[Any, Any]]] = {}

    def __init__(self) -> None:
        self._values: dict[str, Any] = dict.fromkeys(self._resources, ValueNotInitialized)
        self.exit_stack: Final[AsyncExitStack] = AsyncExitStack()

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
        try:
            for name, handler in self._resources.items():
                value = await self.exit_stack.enter_async_context(handler.acquire(self))
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
        res = await self.exit_stack.__aexit__(*exc)
        return res
