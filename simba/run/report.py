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
