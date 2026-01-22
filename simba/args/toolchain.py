from pathlib import Path
from typing import List, NamedTuple

from pydantic import BaseModel


class RawToolchain(BaseModel):
    path: str | None = None
    cflags: str | None = None

    def __or__(self, that: "RawToolchain") -> "RawToolchain":
        def coaelse(lhs, rhs):
            return lhs if lhs is not None else rhs

        return RawToolchain(
            path=coaelse(self.path, that.path),
            cflags=coaelse(self.cflags, "") + " " + coaelse(that.cflags, ""),
        )


class Toolchain(NamedTuple):
    path: Path
    cflags: str

    def __repr__(self) -> str:
        return f"path '{str(self.path)}' cflags '{self.cflags}'"

    @classmethod
    def from_raw(cls, raw: RawToolchain) -> "Toolchain":
        def unwrap(x, name):
            if x is not None:
                return x
            else:
                raise ValueError(f"expected a {name}, but got none")

        return Toolchain(
            path=Path(unwrap(raw.path, "path")),
            cflags=unwrap(raw.cflags, "cflags"),
        )


ToolchainMatrix = List[Toolchain]
