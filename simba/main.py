from typing import Iterable

from simba.args.argv import (
    Args,
    RunExecutableArgs,
    RunMiniprojectArgs,
    RunSourcesArgs,
    RunSuiteArgs,
    TArgs,
)
from simba.run.executable import run_executable
from simba.run.miniproject import run_miniproject
from simba.run.report import ReportedRun
from simba.run.sources import run_sources
from simba.run.suite import run_suite
from simba.verilator.core import Verilator
from simba.log import loggy


def iterating_run(args: Args) -> Iterable[ReportedRun]:
    verilator = Verilator(args.common.verilator_path)

    if isinstance(args.run, RunExecutableArgs):
        yield run_executable(verilator, args.run)
    elif isinstance(args.run, RunSourcesArgs):
        for x in run_sources(verilator, TArgs(args.common, args.run)):
            yield x
    elif isinstance(args.run, RunMiniprojectArgs):
        for x in run_miniproject(verilator, TArgs(args.common, args.run)):
            yield x
    elif isinstance(args.run, RunSuiteArgs):
        for x in run_suite(verilator, TArgs(args.common, args.run)):
            yield x
    else:
        raise RuntimeError(f"unexpected type: {type(args.run)}")


def main():
    try:
        args = Args.from_argv()
        loggy.info("Parsed %s", args)

        runs = list(iterating_run(args))
        print(runs)

    except Exception as e:
        loggy.error(e)

    except KeyboardInterrupt as e:
        loggy.error("Interrupted")

    finally:
        pass


if __name__ == "__main__":
    main()
