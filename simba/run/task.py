from typing import Iterable, NamedTuple

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

        timer = Stopwatch()
        with timer:
            (instrs, cycles) = task.verilator.run_simple(p.executable_path)

        return Report(
            name=p.name,
            toolchain=p.toolchain,
            instrunctions_count=instrs,
            cycles_count=cycles,
            simulation_time=timer.duration,
        )
