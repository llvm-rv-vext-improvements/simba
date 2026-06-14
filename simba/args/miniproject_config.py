from typing import NamedTuple, List
from pathlib import Path

from simba.args.benchmark_input import BenchmarkInput
from simba.args.toolchain import Toolchain


class MiniProjectConfig(NamedTuple):
    toolchain: Toolchain
    sources: List[Path]
    name: str | None
    is_cleaning: bool
    input_: BenchmarkInput | None = None
    show_benchmark: bool = False
