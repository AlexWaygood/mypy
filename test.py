from dataclasses import dataclass, field


def foo(func): ...

@dataclass
class Foo:
    @foo
    def c(self) -> int:
        return 0

    c: int = field(init=False, default=c)
