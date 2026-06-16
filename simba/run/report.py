from datetime import timedelta
from typing import NamedTuple

from pydantic import BaseModel

from simba.args.toolchain import RawToolchain, Toolchain
from simba.args.input_data import (
    RawFunctionInfo,
    RawIterationsInfo,
)
from simba.args.benchmark_input import (
    BenchmarkInput,
    RawBenchmarkInput,
    RawBenchmarkVar,
)


class AdjustmentCounts(NamedTuple):
    total: int
    warmup: int
    main: int


class Adjustment(NamedTuple):
    instrs: AdjustmentCounts
    cycles: AdjustmentCounts


class ReportDetails(NamedTuple):
    adjustment: Adjustment


class Report(NamedTuple):
    name: str
    toolchain: Toolchain | None
    benchmark_config: BenchmarkInput | None
    instrunctions_count: int
    cycles_count: int
    simulation_time: timedelta
    is_customly_trampolined: bool
    details: ReportDetails | None = None


class RawAdjustmentCounts(BaseModel):
    total: int
    warmup: int
    main: int


class RawAdjustment(BaseModel):
    instrs: RawAdjustmentCounts
    cycles: RawAdjustmentCounts


class RawReportDetails(BaseModel):
    adjustment: RawAdjustment


class RawReport(BaseModel):
    name: str
    toolchain: RawToolchain | None = None
    benchmark_config: RawBenchmarkInput | None = None
    instrunctions_count: int
    cycles_count: int
    is_customly_trampolined: bool = False
    details: RawReportDetails | None = None

    def to_pure(self) -> Report:
        details = None
        if self.details:
            adj = self.details.adjustment
            details = ReportDetails(
                adjustment=Adjustment(
                    instrs=AdjustmentCounts(
                        total=adj.instrs.total,
                        warmup=adj.instrs.warmup,
                        main=adj.instrs.main,
                    ),
                    cycles=AdjustmentCounts(
                        total=adj.cycles.total,
                        warmup=adj.cycles.warmup,
                        main=adj.cycles.main,
                    ),
                )
            )
        return Report(
            name=self.name,
            toolchain=Toolchain.from_raw(self.toolchain) if self.toolchain else None,
            benchmark_config=(
                BenchmarkInput.from_raw(self.benchmark_config)
                if self.benchmark_config
                else None
            ),
            instrunctions_count=self.instrunctions_count,
            cycles_count=self.cycles_count,
            simulation_time=timedelta(0),
            is_customly_trampolined=self.is_customly_trampolined,
            details=details,
        )

    @classmethod
    def from_pure(cls, pure: Report) -> "RawReport":
        raw_toolchain = None
        if pure.toolchain:
            raw_toolchain = RawToolchain(
                path=str(pure.toolchain.path),
                cc=pure.toolchain.cc,
                ld=pure.toolchain.ld,
                cflags=pure.toolchain.cflags,
            )
        raw_benchmark_config = None
        if pure.benchmark_config:
            raw_benchmark_config = RawBenchmarkInput(
                function=RawFunctionInfo(
                    name=pure.benchmark_config.function.name,
                    return_type=pure.benchmark_config.function.return_type,
                ),
                iterations=RawIterationsInfo(
                    warmup=pure.benchmark_config.iterations.warmup,
                    main=pure.benchmark_config.iterations.main,
                ),
                vars=[
                    RawBenchmarkVar(
                        variable=var_.variable,
                        input_path=str(var_.input_path),
                        var_type=var_.var_type,
                    )
                    for var_ in pure.benchmark_config.vars
                ],
            )

        raw_details = None
        if pure.details:
            adj = pure.details.adjustment
            raw_details = RawReportDetails(
                adjustment=RawAdjustment(
                    instrs=RawAdjustmentCounts(
                        total=adj.instrs.total,
                        warmup=adj.instrs.warmup,
                        main=adj.instrs.main,
                    ),
                    cycles=RawAdjustmentCounts(
                        total=adj.cycles.total,
                        warmup=adj.cycles.warmup,
                        main=adj.cycles.main,
                    ),
                )
            )

        return RawReport(
            name=pure.name,
            toolchain=raw_toolchain,
            benchmark_config=raw_benchmark_config,
            instrunctions_count=pure.instrunctions_count,
            cycles_count=pure.cycles_count,
            is_customly_trampolined=pure.is_customly_trampolined,
            details=raw_details,
        )
