from pathlib import Path
from typing import List, NamedTuple
from pydantic import BaseModel, FilePath, DirectoryPath, Field, field_validator

from simba.args.parse_json import parse_json


class RawVar(BaseModel):
    name: str
    type_: str = Field(alias="type")
    input_name: str


class RawInputFile(BaseModel):
    name: str
    input_file: FilePath

    @field_validator("input_file")
    @classmethod
    def input_file_must_be_h_ext(cls, v: FilePath) -> FilePath:
        # Check if the string ends with specific substring
        if v.suffix != (".h"):
            raise ValueError("Input files should be .h files")
        return v


class RawInputsDir(BaseModel):
    inputs_dir: DirectoryPath


class RawFunctionInfo(BaseModel):
    name: str
    return_type: str


class RawIterationsInfo(BaseModel):
    warmup: int = 0
    main: int = 0


class RawTestCase(BaseModel):
    vars: List[RawVar]
    function: RawFunctionInfo
    iterations: RawIterationsInfo


class RawInputDataConfig(BaseModel):
    input_files: List[RawInputFile] | None = None
    input_dirs: List[RawInputsDir] | None = None
    test_matrix: List[RawTestCase] | None = None

    @classmethod
    def read_json(cls, path: Path) -> "RawInputDataConfig":
        if not path.exists() or path.is_dir():
            raise ValueError("Path either does not exist or is directory")
        return parse_json(cls, path)


class Var(NamedTuple):
    name: str
    type_: str
    input_name: str

    @classmethod
    def from_raw(cls, raw: RawVar) -> "Var":
        return Var(
            name=raw.name,
            input_name=raw.input_name,
            type_=raw.type_,
        )


class Input(NamedTuple):
    name: str
    input_file: FilePath

    @classmethod
    def from_raw_file(cls, raw: RawInputFile) -> "Input":
        return Input(name=raw.name, input_file=raw.input_file)

    @classmethod
    def from_raw_dir(cls, raw: RawInputsDir) -> List["Input"]:
        inputs = []
        for file in raw.inputs_dir.iterdir():
            if file.is_file() and file.name.endswith(".h"):
                inputs.append(
                    Input.from_raw_file(
                        RawInputFile(
                            name=file.stem,
                            input_file=file.resolve(),
                        ),
                    )
                )
        return inputs


class FunctionInfo(NamedTuple):
    name: str
    return_type: str

    @classmethod
    def from_raw(cls, raw: RawFunctionInfo) -> "FunctionInfo":
        return FunctionInfo(name=raw.name, return_type=raw.return_type)


class IterationsInfo(NamedTuple):
    warmup: int = 0
    main: int = 0

    @classmethod
    def from_raw(cls, raw: RawIterationsInfo) -> "IterationsInfo":
        return IterationsInfo(
            warmup=raw.warmup,
            main=raw.main,
        )


class TestCase(NamedTuple):
    vars: List[Var]
    function: FunctionInfo
    iterations: IterationsInfo

    @classmethod
    def from_raw(cls, raw: RawTestCase) -> "TestCase":
        return TestCase(
            vars=list(map(Var.from_raw, raw.vars)),
            function=FunctionInfo.from_raw(raw.function),
            iterations=IterationsInfo.from_raw(raw.iterations),
        )


class InputDataConfig(NamedTuple):
    inputs: List[Input]
    test_matrix: List[TestCase]

    def validate_var_inputs(self) -> None:
        input_names = {elem.name for elem in self.inputs}
        unexpected_inputs = set()
        for test_case in self.test_matrix:
            unexpected_inputs.update(
                set(var.input_name for var in test_case.vars).difference(input_names)
            )

        if len(unexpected_inputs) != 0:
            vars_with_unexpected_inputs = {
                var.name
                for test_case in self.test_matrix
                for var in test_case.vars
                if var.input_name in unexpected_inputs
            }
            raise ValueError(
                f"Not declared inputs: {unexpected_inputs} "
                f"used by vars: {vars_with_unexpected_inputs}"
            )

    @classmethod
    def from_raw(cls, raw: RawInputDataConfig) -> "InputDataConfig":
        inputs = []

        for file_input in raw.input_files or []:
            inputs.append(Input.from_raw_file(file_input))

        for dir_input in raw.input_dirs or []:
            inputs.extend(Input.from_raw_dir(dir_input))

        config = InputDataConfig(
            inputs=inputs,
            test_matrix=list(map(TestCase.from_raw, raw.test_matrix or [])),
        )

        config.validate_var_inputs()
        return config


# ====================


class BenchmarkVar(NamedTuple):
    variable: str
    type_: str
    input_path: FilePath


class FunctionInput(NamedTuple):
    name: str
    return_type: str


class IterationsInput(NamedTuple):
    warmup: int
    main: int


class BenchmarkInput(NamedTuple):
    function: FunctionInput
    iterations: IterationsInput
    vars: List[BenchmarkVar]


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
                    vars=[],
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
                vars=new_vars,
            )
        )

    return test_inputs
