from pathlib import Path
from typing import List, NamedTuple

from pydantic import BaseModel, FilePath, DirectoryPath


class RawVar(BaseModel):
    var_name: str
    input_name: str

class RawInputFile(BaseModel):
    name: str
    input_file: FilePath # TODO add validation for ".h" files

class RawInputsDir(BaseModel):
    inputs_dir: DirectoryPath

class RawTestCase(BaseModel):
    vars: List[RawVar]
    function_name: str

class RawInputDataConfig(BaseModel):
    input_files: List[RawInputFile] | None = None
    input_dirs: List[RawInputsDir] | None = None
    testMatrix: List[RawTestCase] | None = None

    # TODO validation
    def validate_vars():
        pass

    def validate_func_name():
        pass

class Var(NamedTuple):
    var_name: str
    input_name: str

    @classmethod
    def from_raw(cls, raw: RawVar) -> "Var":
        return Var(
            var_name=raw.var_name,
            input_name=raw.input_name
        )

class Input(NamedTuple):
    name: str
    input_file: FilePath

    @classmethod
    def from_raw_file(cls, raw: RawInputFile) -> "Input":
        return Input(
            name=raw.name,
            input_file=raw.input_file
        )

    @classmethod
    def from_raw_dir(cls, raw: RawInputsDir) -> List["Input"]:
        inputs = []
        for file in raw.inputs_dir.iterdir():
            if file.is_file() and file.name.endswith(".h"):
                inputs.append(
                    Input.from_raw_file(
                        RawInputFile(
                            name=file.name[:len(file.name) - 2], # Removing ".h" for name
                            input_file=file.resolve()
                        ),
                    )
                )

class TestCase(NamedTuple):
    vars: List[Var]
    function_name: str  # TODO make validation that function exists in test case in actual code (Not here)
 
    @classmethod
    def from_raw(cls, raw: RawTestCase) -> "TestCase":
        return TestCase(
            vars=list(map(raw.vars, Var.from_raw)),
            function_name=raw.function_name
        )

class InputDataConfig(NamedTuple):
    inputs: List[Input] | None
    testMatrix: List[TestCase] | None

    @classmethod
    def from_raw(cls, raw: RawInputDataConfig) -> "InputDataConfig":
        inputs = []

        for file_input in raw.input_files or []:
            inputs.append(
                Input.from_raw_file(file_input)
            )
        
        for dir_input in raw.input_dirs or []:
            inputs.append(
                Input.from_raw_dir(dir_input)
            )

        return InputDataConfig(
            inputs=None if len(inputs) == 0 else inputs,
            testMatrix= None if raw.testMatrix is None else list(map(raw.testMatrix, TestCase.from_raw))
        )