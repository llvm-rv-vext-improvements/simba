from pathlib import Path
from typing import List, NamedTuple, Tuple
from pydantic import BaseModel, Field

from simba.args.input_data import RawFunctionInfo, RawIterationsInfo, InputDataConfig


class RawBenchmarkVar(BaseModel):
    variable: str
    input_path: str
    var_type: str = Field(alias="var_type")


class RawBenchmarkInput(BaseModel):
    function: RawFunctionInfo
    iterations: RawIterationsInfo
    vars: List[RawBenchmarkVar]


class BenchmarkVar(NamedTuple):
    variable: str
    var_type: str
    input_path: Path

    @classmethod
    def from_raw(cls, raw: RawBenchmarkVar) -> "BenchmarkVar":
        return BenchmarkVar(
            variable=raw.variable,
            var_type=raw.var_type,
            input_path=Path(raw.input_path),
        )


class FunctionInput(NamedTuple):
    name: str
    return_type: str

    @classmethod
    def from_raw(cls, raw: RawFunctionInfo) -> "FunctionInput":
        return FunctionInput(name=raw.name, return_type=raw.return_type)


class IterationsInput(NamedTuple):
    warmup: int
    main: int

    @classmethod
    def from_raw(cls, raw: RawIterationsInfo) -> "IterationsInput":
        return IterationsInput(
            warmup=raw.warmup,
            main=raw.main,
        )


class BenchmarkInput(NamedTuple):
    function: FunctionInput
    iterations: IterationsInput
    vars: Tuple[BenchmarkVar, ...]

    def to_csv_str(self) -> str:
        func_str = f"{self.function.name}({self.function.return_type})"
        iter_str = f"{self.iterations.warmup}/{self.iterations.main}"
        var_strs = [f"{v.variable}:{v.var_type}:{v.input_path.name}" for v in self.vars]
        vars_str = f"[{', '.join(var_strs)}]"
        return f"{func_str} | iters={iter_str} | vars={vars_str}"

    @classmethod
    def from_raw(cls, raw: RawBenchmarkInput) -> "BenchmarkInput":
        return BenchmarkInput(
            function=FunctionInput.from_raw(raw.function),
            iterations=IterationsInput.from_raw(raw.iterations),
            vars=tuple(BenchmarkVar.from_raw(var_) for var_ in raw.vars),
        )


type BenchmarkInputs = List[BenchmarkInput]


def get_test_inputs(config: InputDataConfig | None) -> BenchmarkInputs:
    if config is None or config.test_matrix is None:
        return []

    test_inputs = []
    for test_case in config.test_matrix:
        function = FunctionInput(
            name=test_case.function.name, return_type=test_case.function.return_type
        )
        iterations = IterationsInput(
            warmup=test_case.iterations.warmup, main=test_case.iterations.main
        )
        if config.inputs is None:
            test_inputs.append(
                BenchmarkInput(
                    function=function,
                    iterations=iterations,
                    vars=tuple(),
                )
            )
            continue

        new_vars = []
        for var in test_case.vars:
            for input_ in config.inputs:
                if var.input_name == input_.name:
                    new_vars.append(
                        BenchmarkVar(var.name, var.type_, input_.input_file)
                    )
        test_inputs.append(
            BenchmarkInput(
                function=function,
                iterations=iterations,
                vars=tuple(new_vars),
            )
        )

    return test_inputs
