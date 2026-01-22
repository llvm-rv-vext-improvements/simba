from typing import Iterable

from simba.args.argv import RunMiniprojectArgs, RunSuiteArgs, TArgs
from simba.run.miniproject import run_miniproject
from simba.run.report import ReportedRun
from simba.verilator.core import Verilator
from simba.log import loggy

def run_suite(verilator: Verilator, args: TArgs[RunSuiteArgs]) -> Iterable[ReportedRun]:
    subdirs = [f for f in args.run.path.iterdir() if f.is_dir()]
    loggy.info(f"Going to run {', '.join(map(str, subdirs))}")

    for subdir in subdirs:
        yield from run_miniproject(
            verilator,
            TArgs(
                common=args.common,
                run=RunMiniprojectArgs(path=subdir),
            ),
        )
