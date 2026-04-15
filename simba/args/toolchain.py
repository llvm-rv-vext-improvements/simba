from pathlib import Path
from typing import List, NamedTuple

from pydantic import BaseModel


class RawToolchain(BaseModel):
    path: str | None = None
    cc: str | None = None
    ld: str | None = None
    cflags: str | None = None

    def __or__(self, that: "RawToolchain") -> "RawToolchain":
        def coalesce(lhs, rhs):
            return lhs if lhs is not None else rhs

        return RawToolchain(
            path=coalesce(self.path, that.path),
            cc=coalesce(self.cc, that.cc),
            ld=coalesce(self.ld, that.ld),
            cflags=coalesce(self.cflags, "") + " " + coalesce(that.cflags, ""),
        )


class Toolchain(NamedTuple):
    path: Path
    cc: str
    ld: str
    cflags: str

    def __repr__(self) -> str:
        return f"path '{str(self.path)}' cc '{self.cc}' ld '{self.ld}' cflags '{self.cflags}'"

    @classmethod
    def from_raw(cls, raw: RawToolchain) -> "Toolchain":
        def unwrap(x, name):
            if x is not None:
                return x

            raise ValueError(f"expected a {name}, but got none")

        return Toolchain(
            path=Path(unwrap(raw.path, "path")),
            cc=unwrap(raw.cc, "cc"),
            ld=unwrap(raw.ld, "ld"),
            cflags=unwrap(raw.cflags, "cflags"),
        )


ToolchainMatrix = List[Toolchain]
