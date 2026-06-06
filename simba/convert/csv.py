from typing import Dict, Iterable, List, NamedTuple, Tuple, Optional

from simba.args.toolchain import Toolchain
from simba.run.report import Report
from simba.args.input_data import BenchmarkInput


class Measurement(NamedTuple):
    toolchain: Toolchain
    instrs: int
    cycles: int
    is_customly_trampolined: bool


class BenchmarkRow(NamedTuple):
    name: str
    config: BenchmarkInput | None 
    measurements: List[Measurement]


class DiffMeasurement(NamedTuple):
    toolchain: Toolchain
    instrs: int
    instrs_diff_abs: int
    instrs_diff_rel: float
    cycles: int
    cycles_diff_abs: int
    cycles_diff_rel: float


class DiffBenchmarkRow(NamedTuple):
    name: str
    config: BenchmarkInput | None
    base: Measurement
    diffs: List[DiffMeasurement]


def reports_to_table(reports: List[Report]) -> Iterable[BenchmarkRow]:
    groups: Dict[Tuple[str, Optional[BenchmarkInput]], List[Report]] = {}
    for report in reports:
        key = (report.name, report.benchmark_config)
        groups.setdefault(key, []).append(report)

    for (name, config), rep_list in groups.items():
        measurements = []
        for rep in rep_list:
            if rep.toolchain is None:
                raise ValueError(f"unexpected empty toolchain in report {rep.name}")
            measurements.append(
                Measurement(
                    toolchain=rep.toolchain,
                    instrs=rep.instrunctions_count,
                    cycles=rep.cycles_count,
                    is_customly_trampolined=rep.is_customly_trampolined,
                )
            )
        yield BenchmarkRow(name=name, config=config, measurements=measurements)


def table_to_diff(table: Iterable[BenchmarkRow]) -> Iterable[DiffBenchmarkRow]:
    def div(a, b):
        return 0 if b == 0 else a / b

    for row in table:
        if not row.measurements:
            continue
        base = row.measurements[0]
        yield DiffBenchmarkRow(
            name=row.name,
            config=row.config,
            base=base,
            diffs=[
                DiffMeasurement(
                    toolchain=m.toolchain,
                    instrs=m.instrs,
                    instrs_diff_abs=m.instrs - base.instrs,
                    instrs_diff_rel=div(m.instrs - base.instrs, base.instrs),
                    cycles=m.cycles,
                    cycles_diff_abs=m.cycles - base.cycles,
                    cycles_diff_rel=div(m.cycles - base.cycles, base.cycles),
                )
                for m in row.measurements[1:]
            ],
        )


def table_to_csv(table: Iterable[DiffBenchmarkRow]) -> str:
    table = list(table)

    rows = []

    # Header
    header_parts = ["Name", "BenchmarkConfig"]

    # Base column
    header_parts.extend(["Conf0", "Instrs0", "Cycles0", "IsTrampolined0"])

    # Diff columns
    max_diffs = max((len(row.diffs) for row in table), default=0)
    for i in range(1, max_diffs + 1):
        header_parts.extend(
            [
                f"Conf{i}",
                f"Instrs{i}",
                f"DInstrsAbs{i}",
                f"DInstrsRel{i}",
                f"Cycles{i}",
                f"DCyclesAbs{i}",
                f"DCyclesRel{i}",
            ]
        )

    rows.append(",".join(header_parts))

    # Data rows
    for row in table:
        config_str = row.config.to_csv_str() if row.config else ""
        data_parts = [row.name, config_str]

        # Base measurement
        data_parts.extend(
            [
                repr(row.base.toolchain),
                str(row.base.instrs),
                str(row.base.cycles),
                str(row.base.is_customly_trampolined),
            ]
        )

        # Diff measurements
        for diff in row.diffs:
            data_parts.extend(
                [
                    repr(diff.toolchain),
                    str(diff.instrs),
                    str(diff.instrs_diff_abs),
                    f"{diff.instrs_diff_rel:.2f}",
                    str(diff.cycles),
                    str(diff.cycles_diff_abs),
                    f"{diff.cycles_diff_rel:.2f}",
                ]
            )

        # Fill empty columns if this row has fewer diffs
        for _ in range(len(row.diffs), max_diffs):
            data_parts.extend([""] * 7)

        rows.append(",".join(data_parts))

    return "\n".join(rows)
