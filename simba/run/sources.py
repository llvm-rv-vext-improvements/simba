from typing import Iterable

from simba.args.argv import RunSourcesArgs, TArgs
from simba.make.miniproject import MiniProject
from simba.run.report import ReportedRun
from simba.verilator.core import Verilator


def run_sources(
    verilator: Verilator,
    args: TArgs[RunSourcesArgs],
) -> Iterable[ReportedRun]:
    if len(args.common.toolchains) <= 0:
        raise ValueError(f"expected at least one toolchain, but got 0")

    for toolchain in args.common.toolchains:
        with MiniProject(
            toolchain=toolchain,
            sources=args.run.paths,
            name=None,
            is_cleaning=False,
        ) as p:
            p.build()
            (instrs, cycles) = verilator.run_simple(p.executable_path)

            yield ReportedRun(
                name=p.name,
                toolchain=toolchain,
                instrunctions_count=instrs,
                cycles_count=cycles,
            )
