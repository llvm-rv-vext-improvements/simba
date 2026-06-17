from typing import Iterable, NamedTuple

from simba.args.benchmark_input import BenchmarkInput
from simba.log import loggy
from simba.make.miniproject import MiniProject
from simba.run.report import Report
from simba.stopwatch import Stopwatch
from simba.verilator.core import Verilator


class Task(NamedTuple):
    verilator: Verilator
    project: MiniProject
    report_config: BenchmarkInput | None = None


Plan = Iterable[Task]


def execute_task(task: Task) -> Report:
    with task.project as p:
        p.build()

        loggy.info("Running %s using %s...", p.executable_path, repr(p.toolchain))

        timer = Stopwatch()
        with timer:
            (instrs, cycles) = task.verilator.run_simple(p.executable_path)

        loggy.info(
            "Executed '%s' by %s, spent %ss real time, got %s cycles, %s instrs",
            p.name,
            p.toolchain,
            round(timer.duration.total_seconds()),
            cycles,
            instrs,
        )

        return Report(
            name=p.name,
            toolchain=p.toolchain,
            benchmark_config=(
                task.report_config
                if task.report_config is not None
                else p.benchmark_input
            ),
            instrunctions_count=instrs,
            cycles_count=cycles,
            simulation_time=timer.duration,
            is_customly_trampolined=p.is_trampoline_present,
        )
