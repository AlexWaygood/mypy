from typing import *

_T = TypeVar("_T")
_U = TypeVar("_U")
_V = TypeVar("_V")
_W = TypeVar("_W")
_P = ParamSpec("_P")

@overload
def call(
    _func: Callable[Concatenate[_T, _P], _U],
    _x: _T,
    *args: Any,
    **kwargs: Any,
) -> _U: ...
@overload
def call(
    _func: Callable[Concatenate[_T, _U, _P], _V],
    _x: _T,
    _y: _U,
    *args: Any,
    **kwargs: Any,
) -> _V: ...
