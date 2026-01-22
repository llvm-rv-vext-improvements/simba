from datetime import timedelta
from pathlib import Path
from typing import NamedTuple

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

    def to_pure(self) -> Report:
        if self.toolchain is None:
            raise ValueError("RawReport: toolchain should be set")
        if self.toolchain.path is None:
            raise ValueError("RawReport: toolchain.path should be set")
        if self.toolchain.cflags is None:
            raise ValueError("RawReport: toolchain.cflags should be set")

        return Report(
            name=self.name,
            toolchain=Toolchain(
                path=Path(self.toolchain.path),
                cflags=self.toolchain.cflags,
            ),
            instrunctions_count=self.instrunctions_count,
            cycles_count=self.cycles_count,
            simulation_time=timedelta(0),
        )

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
