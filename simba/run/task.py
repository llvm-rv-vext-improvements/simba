from typing import Iterable, NamedTuple

from simba.log import loggy
from simba.make.miniproject import MiniProject
from simba.run.report import Report
from simba.stopwatch import Stopwatch
from simba.verilator.core import Verilator


class Task(NamedTuple):
    verilator: Verilator
    project: MiniProject


Plan = Iterable[Task]


def execute_task(task: Task) -> Report:
    with task.project as p:
        p.build()

        loggy.info("Running %s...", p.executable_path)

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
            instrunctions_count=instrs,
            cycles_count=cycles,
            simulation_time=timer.duration,
        )
