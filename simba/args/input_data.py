from pathlib import Path
from typing import List, NamedTuple, Optional
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


class RawTestCase(BaseModel):
    vars: List[RawVar]
    function_name: str
    function_return_type: str


class RawInputDataConfig(BaseModel):
    input_files: List[RawInputFile] | None = None
    input_dirs: List[RawInputsDir] | None = None
    test_matrix: List[RawTestCase] | None = None

    @classmethod
    def resolve_path(cls, *, path: Path | None = None) -> Path:
        if path is not None:
            return path
        return Path("./.input.simba.json")

    @classmethod
    def read_json(cls, path: Path) -> Optional["RawInputDataConfig"]:
        if not path.exists():
            return None
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


class TestCase(NamedTuple):
    vars: List[Var]
    function_name: str
    function_return_type: str

    @classmethod
    def from_raw(cls, raw: RawTestCase) -> "TestCase":
        return TestCase(
            vars=list(map(Var.from_raw, raw.vars)),
            function_name=raw.function_name,
            function_return_type=raw.function_return_type,
        )


class InputDataConfig(NamedTuple):
    inputs: List[Input] | None
    test_matrix: List[TestCase] | None

    def validate_var_inputs(self) -> None:
        input_names = {elem.name for elem in (self.inputs or [])}
        unexpected_inputs = set()
        for test_case in self.test_matrix or []:
            unexpected_inputs.update(
                set(var.input_name for var in test_case.vars).difference(input_names)
            )

        if len(unexpected_inputs) != 0:
            vars_with_unexpected_inputs = {
                var.name
                for test_case in self.test_matrix or []
                for var in test_case.vars
                if var.input_name in unexpected_inputs
            }
            raise ValueError(
                f"Not declared inputs: {unexpected_inputs} "
                f"used by vars: {vars_with_unexpected_inputs}"
            )

    @classmethod
    def from_raw(cls, raw: RawInputDataConfig | None) -> Optional["InputDataConfig"]:
        if raw is None:
            return None

        inputs = []

        for file_input in raw.input_files or []:
            inputs.append(Input.from_raw_file(file_input))

        for dir_input in raw.input_dirs or []:
            inputs.extend(Input.from_raw_dir(dir_input))

        config = InputDataConfig(
            inputs=None if len(inputs) == 0 else inputs,
            test_matrix=(
                None
                if raw.test_matrix is None
                else list(map(TestCase.from_raw, raw.test_matrix))
            ),
        )

        config.validate_var_inputs()
        return config


# ====================


class TestVar(NamedTuple):
    variable: str
    type_: str
    input_path: FilePath


class TestInput(NamedTuple):
    function_name: str
    function_return_type: str
    vars: List[TestVar]


type TestInputs = List[TestInput]


def get_test_inputs(config: InputDataConfig | None) -> TestInputs:
    if config is None or config.test_matrix is None:
        return []

    test_inputs = []
    for test_case in config.test_matrix:
        if config.inputs is None:
            test_inputs.append(
                TestInput(
                    function_name=test_case.function_name,
                    function_return_type=test_case.function_return_type,
                    vars=[],
                )
            )
            continue

        new_vars = []
        for var in test_case.vars:
            for input_ in config.inputs:
                if var.input_name == input_.name:
                    new_vars.append(TestVar(var.name, var.type_, input_.input_file))
        test_inputs.append(
            TestInput(
                function_name=test_case.function_name,
                function_return_type=test_case.function_return_type,
                vars=new_vars,
            )
        )

    return test_inputs
