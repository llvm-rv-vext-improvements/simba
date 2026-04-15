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
    is_customly_trampolined: bool


class RawReport(BaseModel):
    name: str
    toolchain: RawToolchain | None = None
    instrunctions_count: int
    cycles_count: int
    is_customly_trampolined: bool = False

    def to_pure(self) -> Report:
        if self.toolchain is None:
            raise ValueError("RawReport: toolchain should be set")
        if self.toolchain.path is None:
            raise ValueError("RawReport: toolchain.path should be set")
        if self.toolchain.cc is None:
            raise ValueError("RawReport: toolchain.cc should be set")
        if self.toolchain.ld is None:
            raise ValueError("RawReport: toolchain.ld should be set")
        if self.toolchain.cflags is None:
            raise ValueError("RawReport: toolchain.cflags should be set")

        return Report(
            name=self.name,
            toolchain=Toolchain(
                path=Path(self.toolchain.path),
                cc=self.toolchain.cc,
                ld=self.toolchain.ld,
                cflags=self.toolchain.cflags,
            ),
            instrunctions_count=self.instrunctions_count,
            cycles_count=self.cycles_count,
            simulation_time=timedelta(0),
            is_customly_trampolined=self.is_customly_trampolined,
        )

    @classmethod
    def from_pure(cls, pure: Report) -> "RawReport":
        raw_toolchain = None
        if pure.toolchain:
            raw_toolchain = RawToolchain(
                path=str(pure.toolchain.path),
                cc=pure.toolchain.cc,
                ld=pure.toolchain.ld,
                cflags=pure.toolchain.cflags,
            )

        return RawReport(
            name=pure.name,
            toolchain=raw_toolchain,
            instrunctions_count=pure.instrunctions_count,
            cycles_count=pure.cycles_count,
            is_customly_trampolined=pure.is_customly_trampolined,
        )
