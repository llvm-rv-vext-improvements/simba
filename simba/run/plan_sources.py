from simba.args.argv import RunSourcesArgs, TArgs
from simba.make.miniproject import MiniProject
from simba.run.task import Plan, Task
from simba.verilator.core import Verilator


def plan_sources(
    verilator: Verilator,
    args: TArgs[RunSourcesArgs],
    name: str | None = None,
) -> Plan:
    if len(args.common.toolchains) <= 0:
        raise ValueError("expected at least one toolchain, but got 0")

    for toolchain in args.common.toolchains:
        yield Task(
            verilator=verilator,
            project=MiniProject(
                toolchain=toolchain,
                sources=args.run.paths,
                name=name,
                is_cleaning=False,
            ),
        )
