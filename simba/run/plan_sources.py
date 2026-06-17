from simba.args.argv import RunSourcesArgs, TArgs
from simba.make.miniproject import MiniProject
from simba.run.adjustment import plan_warmup
from simba.run.task import Plan, Task
from simba.verilator.core import Verilator
from simba.args.miniproject_config import MiniProjectConfig
from simba.args.benchmark_input import get_test_inputs


def plan_sources(
    verilator: Verilator,
    args: TArgs[RunSourcesArgs],
    name: str | None = None,
) -> Plan:
    if len(args.common.toolchains) <= 0:
        raise ValueError("expected at least one toolchain, but got 0")

    for toolchain in args.common.toolchains:
        for input_ in get_test_inputs(args.run.input_data_config) or [None]:
            config = MiniProjectConfig(
                toolchain=toolchain,
                sources=args.run.paths,
                name=name,
                is_cleaning=False,
                input_=input_,
            )
            project = MiniProject(config=config)

            yield from plan_warmup(verilator, project, list(args.run.paths))
            yield Task(verilator=verilator, project=project)
