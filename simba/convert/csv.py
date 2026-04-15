from typing import Dict, Iterable, List, NamedTuple

from simba.args.toolchain import Toolchain
from simba.run.report import Report


class Measurement(NamedTuple):
    toolchain: Toolchain
    instrs: int
    cycles: int
    is_customly_trampolined: bool


class BenchmarkRow(NamedTuple):
    name: str
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
    base: Measurement
    diffs: List[DiffMeasurement]


def reports_to_table(reports: List[Report]) -> Iterable[BenchmarkRow]:
    def unwrap(x, name: str):
        if x is None:
            raise ValueError(f"unexpected empty {name}")
        return x

    reports_by_name: Dict[str, List[Report]] = {}
    for report in reports:
        reports_by_name[report.name] = reports_by_name.get(report.name, [])
        reports_by_name[report.name].append(report)

    for name, enemies in reports_by_name.items():
        yield BenchmarkRow(
            name=name,
            measurements=[
                Measurement(
                    toolchain=unwrap(report.toolchain, "toolchain"),
                    instrs=report.instrunctions_count,
                    cycles=report.cycles_count,
                    is_customly_trampolined=report.is_customly_trampolined,
                )
                for report in enemies
            ],
        )


def table_to_diff(table: Iterable[BenchmarkRow]) -> Iterable[DiffBenchmarkRow]:
    def div(a, b):
        if a == b:
            return 1
        if b == 0:
            return 0
        return a / b

    for row in table:
        b = row.measurements[0]
        yield DiffBenchmarkRow(
            name=row.name,
            base=b,
            diffs=[
                DiffMeasurement(
                    toolchain=m.toolchain,
                    instrs=m.instrs,
                    instrs_diff_abs=m.instrs - b.instrs,
                    instrs_diff_rel=div(m.instrs - b.instrs, b.instrs),
                    cycles=m.cycles,
                    cycles_diff_abs=m.cycles - b.cycles,
                    cycles_diff_rel=div(m.cycles - b.cycles, b.cycles),
                )
                for m in row.measurements[1:]
            ],
        )


def table_to_csv(table: Iterable[DiffBenchmarkRow]) -> str:
    table = list(table)

    rows = []

    # Header
    header_parts = ["Name"]

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
        data_parts = [row.name]

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
            data_parts.extend([""] * 7)  # 7 columns per diff

        rows.append(",".join(data_parts))

    return "\n".join(rows)
