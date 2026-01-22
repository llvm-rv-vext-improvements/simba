from typing import Iterable

from simba.args.argv import RunMiniprojectArgs, RunSourcesArgs, TArgs
from simba.run.report import ReportedRun
from simba.run.sources import run_sources
from simba.verilator.core import Verilator


def to_sources_args(args: TArgs[RunMiniprojectArgs]) -> TArgs[RunSourcesArgs]:
    paths = [f.resolve() for f in args.run.path.iterdir()]
    return TArgs(common=args.common, run=RunSourcesArgs(paths=paths))


def run_miniproject(
    verilator: Verilator,
    args: TArgs[RunMiniprojectArgs],
) -> Iterable[ReportedRun]:
    def transform(run: ReportedRun) -> ReportedRun:
        return run._replace(name=args.run.path.name)

    return map(transform, run_sources(verilator, to_sources_args(args)))
