from simba.args.argv import RunExecutableArgs
from simba.run.report import Report
from simba.stopwatch import Stopwatch
from simba.verilator.core import Verilator


def run_executable(verilator: Verilator, args: RunExecutableArgs) -> Report:
    timer = Stopwatch()
    with timer:
        (instrs, cycles) = verilator.run_simple(args.path)

    return Report(
        name=args.path.name,
        toolchain=None,
        instrunctions_count=instrs,
        cycles_count=cycles,
        simulation_time=timer.duration,
    )
