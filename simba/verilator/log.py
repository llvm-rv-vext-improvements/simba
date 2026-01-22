import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import DefaultDict, Iterable, List

Time = int
MetricNamespace = str
MetricName = str
MetricValue = int


@dataclass
class VerilatorLog:
    @dataclass
    class Core:
        core_number: int
        instrunctions_count: int
        cycles_count: int

    @dataclass
    class Brief:
        cores: list["VerilatorLog.Core"] = field(default_factory=list)
        time_spent_ms: int = 0

    Perf = DefaultDict[
        Time,
        DefaultDict[
            MetricNamespace,
            DefaultDict[
                MetricName,
                List[MetricValue],
            ],
        ],
    ]

    brief: Brief = field(default_factory=Brief)
    perf: Perf = field(
        default_factory=lambda: defaultdict(
            lambda: defaultdict(lambda: defaultdict(list))
        )
    )


def verilator_brief_log_parse(lines: Iterable[str]) -> VerilatorLog.Brief:
    instr_cycle_row: re.Pattern = re.compile(
        r".*Core-(\d) instrCnt = (\d+), cycleCnt = (\d+), IPC = \d+.\d+.*"
    )

    time_spent_row: re.Pattern = re.compile(r".*Host time spent: (\d+)ms.*")

    brief = VerilatorLog.Brief()

    for _, line in enumerate(lines, 1):
        line = line.strip()
        if len(line) == 0:
            continue

        if match := instr_cycle_row.match(line):
            core_number = int(match.group(1))
            instr_count = int(match.group(2))
            cycle_count = int(match.group(3))

            brief.cores.append(
                VerilatorLog.Core(
                    core_number=core_number,
                    instrunctions_count=instr_count,
                    cycles_count=cycle_count,
                )
            )
            continue

        if match := time_spent_row.match(line):
            brief.time_spent_ms = int(match.group(1))
            continue

    return brief


def verilator_perf_log_parse(lines: Iterable[str]) -> VerilatorLog.Perf:
    perf_row: re.Pattern = re.compile(
        r"\[PERF \]\[time=\s*(\d+)\]\s*([^:]+):\s*([^,]+),\s*(\d+)"
    )

    perf = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if len(line) == 0:
            continue

        match = perf_row.match(line)
        if not match:
            raise RuntimeError(f"Warning: Could not parse line {i}: {line}")

        time: Time = int(match.group(1))
        path: MetricNamespace = match.group(2).strip()
        name: MetricName = match.group(3).strip()
        value: MetricValue = int(match.group(4))

        perf[time][path][name].append(value)

    return perf
