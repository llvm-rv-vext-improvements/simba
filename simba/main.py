from concurrent.futures import ProcessPoolExecutor
import os
from typing import Iterable, List

from simba.args.argv import (
    Args,
    RunExecutableArgs,
    RunMiniprojectArgs,
    RunSourcesArgs,
    RunSuiteArgs,
    TArgs,
)
from simba.run.run_executable import run_executable
from simba.run.plan_miniproject import plan_miniproject
from simba.run.report import Report
from simba.run.plan_sources import plan_sources
from simba.run.plan_suite import plan_suite
from simba.run.task import Plan, execute_task
from simba.stopwatch import Stopwatch
from simba.verilator.core import Verilator
from simba.log import loggy


def plan(args: Args) -> Plan:
    verilator = Verilator(args.common.verilator_path)

    if isinstance(args.run, RunExecutableArgs):
        raise NotImplementedError
    elif isinstance(args.run, RunSourcesArgs):
        yield from plan_sources(verilator, TArgs(args.common, args.run))
    elif isinstance(args.run, RunMiniprojectArgs):
        yield from plan_miniproject(verilator, TArgs(args.common, args.run))
    elif isinstance(args.run, RunSuiteArgs):
        yield from plan_suite(verilator, TArgs(args.common, args.run))
    else:
        raise RuntimeError(f"unexpected type: {type(args.run)}")


def execute(plan: Plan, j: int = os.cpu_count() or 1) -> Iterable[Report]:
    with ProcessPoolExecutor(max_workers=j) as executor:
        # Preserves an order and it is important!
        yield from executor.map(execute_task, plan)


def main():
    try:
        args = Args.from_argv()
        loggy.debug("Parsed %s", args)

        timer = Stopwatch()
        with timer:
            tasks: Plan = []
            if not isinstance(args.run, RunExecutableArgs):
                tasks = plan(args)

            reports: List[Report] = []
            if isinstance(args.run, RunExecutableArgs):
                verilator = Verilator(args.common.verilator_path)
                report = run_executable(verilator, args.run)
                reports.append(report)

            for report in execute(tasks):
                reports.append(report)

                loggy.info(
                    "Executed '%s' by %s, spent %ss real time, got %s cycles, %s instrs",
                    report.name,
                    report.toolchain,
                    round(report.simulation_time.total_seconds()),
                    report.cycles_count,
                    report.instrunctions_count,
                )

        loggy.info("Total %ss real time spent", round(timer.duration.total_seconds()))

    except Exception as e:
        loggy.error(e)

    except KeyboardInterrupt as e:
        loggy.error("Interrupted")


if __name__ == "__main__":
    main()
