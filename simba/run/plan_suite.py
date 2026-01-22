from simba.args.argv import RunMiniprojectArgs, RunSuiteArgs, TArgs
from simba.run.plan_miniproject import plan_miniproject
from simba.run.task import Plan
from simba.verilator.core import Verilator


def plan_suite(verilator: Verilator, args: TArgs[RunSuiteArgs]) -> Plan:
    subdirs = [f for f in args.run.path.iterdir() if f.is_dir()]

    for subdir in subdirs:
        yield from plan_miniproject(
            verilator,
            TArgs(
                common=args.common,
                run=RunMiniprojectArgs(path=subdir),
            ),
        )
