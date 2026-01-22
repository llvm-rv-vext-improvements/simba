from pathlib import Path
import subprocess

from simba.timer import timer
from simba.verilator.log import (
    VerilatorLog,
    verilator_brief_log_parse,
    verilator_perf_log_parse,
)
from simba.log import loggy


class Verilator:
    def __init__(self, executable_path: Path) -> None:
        self.__executable_path = executable_path

    def run_simple(self, executable: Path) -> tuple[int, int]:
        with timer():
            log = self.run(executable)

        instrs = log.brief.cores[0].instrunctions_count
        cycles = log.brief.cores[0].cycles_count

        loggy.info("Got %s instrs and %s cycles", instrs, cycles)
        return (instrs, cycles)

    def run(self, executable: Path) -> VerilatorLog:
        loggy.info("Running '%s'...", executable)

        command = [
            str(self.__executable_path),
            "--no-diff",
            "-i",
            str(executable),
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(
                f"{' '.join(command)} returned {process.returncode}: {process.stderr}",
            )

        return VerilatorLog(
            brief=verilator_brief_log_parse(stdout.splitlines()),
            perf=verilator_perf_log_parse(stderr.splitlines()),
        )
