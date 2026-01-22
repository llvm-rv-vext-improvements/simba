from concurrent.futures import ProcessPoolExecutor
import json
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
from simba.convert.json import reports_to_json
from simba.run.run_executable import run_executable
from simba.run.plan_miniproject import plan_miniproject
from simba.run.report import RawReport, Report
from simba.run.plan_sources import plan_sources
from simba.run.plan_suite import plan_suite
from simba.run.task import Plan, execute_task
from simba.stopwatch import Stopwatch
from simba.verilator.core import Verilator
from simba.log import loggy


def plan(args: Args) -> Plan:
    verilator = Verilator(args.common.verilator_path)

    if isinstance(args.action, RunExecutableArgs):
        raise NotImplementedError
    elif isinstance(args.action, RunSourcesArgs):
        yield from plan_sources(verilator, TArgs(args.common, args.action))
    elif isinstance(args.action, RunMiniprojectArgs):
        yield from plan_miniproject(verilator, TArgs(args.common, args.action))
    elif isinstance(args.action, RunSuiteArgs):
        yield from plan_suite(verilator, TArgs(args.common, args.action))
    else:
        raise RuntimeError(f"unexpected type: {type(args.action)}")


def execute(plan: Plan, j: int = os.cpu_count() or 1) -> Iterable[Report]:
    with ProcessPoolExecutor(max_workers=j) as executor:
        # Preserves an order and it is important!
        yield from executor.map(execute_task, plan)


def main(args: Args):
    timer = Stopwatch()
    with timer:
        tasks: Plan = []
        if not isinstance(args.action, RunExecutableArgs):
            tasks = plan(args)

        reports: List[Report] = []
        if isinstance(args.action, RunExecutableArgs):
            verilator = Verilator(args.common.verilator_path)
            report = run_executable(verilator, args.action)
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

    print(reports_to_json(reports))
