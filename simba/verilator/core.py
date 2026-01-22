import subprocess
from pathlib import Path

from simba.verilator.log import (VerilatorLog, verilator_brief_log_parse,
                                 verilator_perf_log_parse)


class Verilator:
    def __init__(self, executable_path: Path) -> None:
        self.__executable_path = executable_path

    def run_simple(self, executable: Path) -> tuple[int, int]:
        log = self.run(executable)
        instrs = log.brief.cores[0].instrunctions_count
        cycles = log.brief.cores[0].cycles_count
        return (instrs, cycles)

    def run(self, executable: Path) -> VerilatorLog:
        command = [
            str(self.__executable_path),
            "--no-diff",
            "--max-instr=1000",
            "-i",
            str(executable),
        ]

        with subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as p:
            stdout, stderr = p.communicate()

            if p.returncode != 0:
                raise RuntimeError(
                    f"{' '.join(command)} returned {p.returncode}: {p.stderr}",
                )

        return VerilatorLog(
            brief=verilator_brief_log_parse(stdout.splitlines()),
            perf=verilator_perf_log_parse(stderr.splitlines()),
        )
