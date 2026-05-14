from simba.args.argv import RunMiniprojectArgs, RunSourcesArgs, TArgs
from simba.run.plan_sources import plan_sources
from simba.run.task import Plan
from simba.verilator.core import Verilator
from simba.args.input_data import InputDataConfig, RawInputDataConfig


def to_sources_args(args: TArgs[RunMiniprojectArgs]) -> TArgs[RunSourcesArgs]:
    paths = [f.resolve() for f in args.run.path.iterdir()]

    input_config = args.input_config
    for path_ in paths:
        if path_.name == ".input.simba.json":
            if input_config is None:
                input_config = InputDataConfig.from_raw(
                    RawInputDataConfig.read_json(path_)
                )
            paths.remove(path_)
            break

    return TArgs(
        common=args.common, run=RunSourcesArgs(paths=paths), input_config=input_config
    )


def plan_miniproject(verilator: Verilator, args: TArgs[RunMiniprojectArgs]) -> Plan:
    return plan_sources(verilator, to_sources_args(args), name=args.run.path.name)
