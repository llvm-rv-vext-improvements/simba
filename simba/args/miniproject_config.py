from typing import NamedTuple, List
from pathlib import Path

from simba.args.input_data import BenchmarkInput
from simba.args.toolchain import Toolchain


class MiniProjectConfig(NamedTuple):
    toolchain: Toolchain
    sources: List[Path]
    name: str | None
    is_cleaning: bool
    input_: BenchmarkInput | None = None
