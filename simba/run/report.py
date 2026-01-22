from typing import Dict, List, NamedTuple
from datetime import timedelta

from pydantic import BaseModel

from simba.args.toolchain import RawToolchain, Toolchain


class Report(NamedTuple):
    name: str
    toolchain: Toolchain | None
    instrunctions_count: int
    cycles_count: int
    simulation_time: timedelta


class RawReport(BaseModel):
    name: str
    toolchain: RawToolchain | None = None
    instrunctions_count: int
    cycles_count: int

    @classmethod
    def from_pure(cls, pure: Report) -> "RawReport":
        raw_toolchain = None
        if pure.toolchain:
            raw_toolchain = RawToolchain(
                path=str(pure.toolchain.path),
                cflags=pure.toolchain.cflags,
            )

        return RawReport(
            name=pure.name,
            toolchain=raw_toolchain,
            instrunctions_count=pure.instrunctions_count,
            cycles_count=pure.cycles_count,
        )
