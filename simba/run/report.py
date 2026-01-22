from typing import NamedTuple

from simba.args.toolchain import Toolchain


class ReportedRun(NamedTuple):
    name: str
    toolchain: Toolchain | None
    instrunctions_count: int
    cycles_count: int


class Report(NamedTuple):
    runs: list[ReportedRun]
