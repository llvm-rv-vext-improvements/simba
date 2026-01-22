from simba.args.argv import RunMiniprojectArgs, RunSourcesArgs, TArgs
from simba.run.plan_sources import plan_sources
from simba.run.task import Plan
from simba.verilator.core import Verilator


def to_sources_args(args: TArgs[RunMiniprojectArgs]) -> TArgs[RunSourcesArgs]:
    paths = [f.resolve() for f in args.run.path.iterdir()]
    return TArgs(common=args.common, run=RunSourcesArgs(paths=paths))


def plan_miniproject(verilator: Verilator, args: TArgs[RunMiniprojectArgs]) -> Plan:
    return plan_sources(verilator, to_sources_args(args), name=args.run.path.name)
