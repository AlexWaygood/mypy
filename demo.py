from datetime import UTC, datetime
from typing import Protocol, Self

from injector import Binder, Injector, Module


class NowGenerator(Protocol):
    def __call__(self: Self) -> datetime:
        ...


class NowGeneratorImpl:
    def __call__(self: Self) -> datetime:
        return datetime.now(tz=UTC)


class GeneratorsModule(Module):
    def configure(self: Self, binder: Binder) -> None:
        binder.bind(
            NowGenerator,  # type: ignore[type-abstract]
            to=NowGeneratorImpl,
        )


injector = Injector([GeneratorsModule])
print(injector.get(NowGenerator)())  # type: ignore[type-abstract]
