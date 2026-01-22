from simba.args.argv import RunExecutableArgs
from simba.run.report import ReportedRun
from simba.verilator.core import Verilator

def run_executable(verilator: Verilator, args: RunExecutableArgs) -> ReportedRun:
    (instrs, cycles) = verilator.run_simple(args.path)
    return ReportedRun(
        name=args.path.name,
        toolchain=None,
        instrunctions_count=instrs,
        cycles_count=cycles,
    )
