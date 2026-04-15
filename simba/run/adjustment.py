from pathlib import Path
from typing import List

from simba.args.toolchain import Toolchain
from simba.make.miniproject import MiniProject
from simba.run.report import Report
from simba.run.task import Plan, Task
from simba.verilator.core import Verilator


NOP_TASK_NAME = "__simba_nop"


def is_not_nop(report: Report) -> bool:
    return report.name != NOP_TASK_NAME


def generate_nop_file() -> Path:
    nop_dir = Path("/tmp/simba/support")
    nop_dir.mkdir(parents=True, exist_ok=True)

    nop_file = nop_dir / "nop.c"
    nop_content = "void main() {}\n"

    with open(nop_file, "w", encoding="utf-8") as f:
        f.write(nop_content)

    return nop_file


def plan_nop(
    verilator: Verilator,
    toolchains: List[Toolchain],
) -> Plan:
    if len(toolchains) <= 0:
        raise ValueError("expected at least one toolchain, but got 0")

    nop_file = generate_nop_file()

    for toolchain in toolchains:
        yield Task(
            verilator=verilator,
            project=MiniProject(
                toolchain=toolchain,
                sources=[nop_file],
                name=NOP_TASK_NAME,
                is_cleaning=False,
            ),
        )


def nop_by_toolchain(reports: List[Report]) -> dict[Toolchain, Report]:
    nop_reports = {}
    for report in reports:
        if report.name == NOP_TASK_NAME and report.toolchain is not None:
            nop_reports[report.toolchain] = report
    return nop_reports


def adjust_report(report: Report, nop: Report) -> Report:
    assert report.toolchain == nop.toolchain

    if report.is_customly_trampolined:
        return report

    return Report(
        name=report.name,
        toolchain=report.toolchain,
        instrunctions_count=report.instrunctions_count - nop.instrunctions_count,
        cycles_count=report.cycles_count - nop.cycles_count,
        simulation_time=report.simulation_time,
        is_customly_trampolined=report.is_customly_trampolined,
    )


def adjust_reports(reports: List[Report]) -> List[Report]:
    nop_reports = nop_by_toolchain(reports)

    adjusted = []
    for report in reports:
        if report.toolchain is not None and report.toolchain in nop_reports:
            nop = nop_reports[report.toolchain]
            adjusted.append(adjust_report(report, nop))
        else:
            adjusted.append(report)

    return adjusted
