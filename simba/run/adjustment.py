from pathlib import Path
from typing import List

from simba.args.toolchain import Toolchain
from simba.make.miniproject import MiniProject
from simba.run.report import Adjustment, AdjustmentCounts, Report, ReportDetails
from simba.run.task import Plan, Task
from simba.verilator.core import Verilator
from simba.args.miniproject_config import MiniProjectConfig


NOP_TASK_NAME = "__simba_nop"
WARMUP_TASK_PREFIX = "__simba_warmup_"


def is_not_nop(report: Report) -> bool:
    return report.name != NOP_TASK_NAME


def is_not_warmup(report: Report) -> bool:
    return not report.name.startswith(WARMUP_TASK_PREFIX)


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
        config = MiniProjectConfig(
            toolchain=toolchain,
            sources=[nop_file],
            name=NOP_TASK_NAME,
            is_cleaning=False,
        )
        yield Task(
            verilator=verilator,
            project=MiniProject(config=config),
        )


def plan_warmup(
    verilator: Verilator,
    project: MiniProject,
    sources: List[Path],
) -> Plan:
    input_ = project.benchmark_input
    if input_ is None or input_.iterations.main <= 0:
        return

    config = MiniProjectConfig(
        toolchain=project.toolchain,
        sources=sources,
        name=f"{WARMUP_TASK_PREFIX}{project.name}",
        is_cleaning=False,
        input_=input_,
        is_adjustment=True,
    )

    yield Task(
        verilator=verilator,
        project=MiniProject(config=config),
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

    adjusted_instrs = report.instrunctions_count - nop.instrunctions_count
    adjusted_cycles = report.cycles_count - nop.cycles_count

    return Report(
        name=report.name,
        toolchain=report.toolchain,
        benchmark_config=report.benchmark_config,
        instrunctions_count=adjusted_instrs,
        cycles_count=adjusted_cycles,
        simulation_time=report.simulation_time,
        is_customly_trampolined=report.is_customly_trampolined,
        details=ReportDetails(
            adjustment=Adjustment(
                instrs=AdjustmentCounts(
                    total=report.instrunctions_count,
                    warmup=nop.instrunctions_count,
                    main=adjusted_instrs,
                ),
                cycles=AdjustmentCounts(
                    total=report.cycles_count,
                    warmup=nop.cycles_count,
                    main=adjusted_cycles,
                ),
            )
        ),
    )


def warmup_key(name: str, report: Report) -> tuple:
    return (name, report.toolchain, report.benchmark_config)


def warmup_by_main_key(reports: List[Report]) -> dict:
    result = {}
    for report in reports:
        if report.name.startswith(WARMUP_TASK_PREFIX):
            main_name = report.name[len(WARMUP_TASK_PREFIX) :]
            result[warmup_key(main_name, report)] = report
    return result


def adjust_warmup(report: Report, warmup: Report) -> Report:
    assert report.toolchain == warmup.toolchain

    iters = report.benchmark_config.iterations  # type: ignore[union-attr]

    adjusted_instrs = (
        report.instrunctions_count - warmup.instrunctions_count
    ) // iters.main
    adjusted_cycles = (report.cycles_count - warmup.cycles_count) // iters.main

    return Report(
        name=report.name,
        toolchain=report.toolchain,
        benchmark_config=report.benchmark_config,
        instrunctions_count=adjusted_instrs,
        cycles_count=adjusted_cycles,
        simulation_time=report.simulation_time,
        is_customly_trampolined=report.is_customly_trampolined,
        details=ReportDetails(
            adjustment=Adjustment(
                instrs=AdjustmentCounts(
                    total=report.instrunctions_count,
                    warmup=warmup.instrunctions_count,
                    main=adjusted_instrs,
                ),
                cycles=AdjustmentCounts(
                    total=report.cycles_count,
                    warmup=warmup.cycles_count,
                    main=adjusted_cycles,
                ),
            )
        ),
    )


def adjust_reports(reports: List[Report]) -> List[Report]:
    nop_reports = nop_by_toolchain(reports)
    warmup_reports = warmup_by_main_key(reports)

    adjusted = []
    for report in filter(is_not_nop, filter(is_not_warmup, reports)):
        key = warmup_key(report.name, report)
        if key in warmup_reports:
            adjusted.append(adjust_warmup(report, warmup_reports[key]))
        elif report.toolchain is not None and report.toolchain in nop_reports:
            adjusted.append(adjust_report(report, nop_reports[report.toolchain]))
        else:
            adjusted.append(report)

    return adjusted
