from typing import Callable, Protocol, TypeVar, overload
from typing_extensions import ParamSpec, TypeAlias

_P = ParamSpec("_P")
_R_co = TypeVar("_R_co", covariant=True)
_Handler: TypeAlias = Callable[_P, _R_co]

class _HandlerDecorator(Protocol):
    def __call__(self, handler: _Handler[_P, _R_co]) -> _Handler[_P, _R_co]: ...

@overload
def event(event_handler: _Handler[_P, _R_co]) -> _Handler[_P, _R_co]: ...
@overload
def event(namespace: str, *args, **kwargs) -> _HandlerDecorator: ...
