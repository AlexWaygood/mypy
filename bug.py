from collections.abc import Callable
from typing import _P as P, Concatenate


def f(c: Callable[[int], None], /, i: int) -> None:
    c(i)

def d(fn: Callable[Concatenate[Callable[P, None], P], None]) -> None:
    fn

d(f)
