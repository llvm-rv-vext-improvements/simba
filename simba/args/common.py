from pathlib import Path
from typing import List, NamedTuple

from pydantic import BaseModel, ValidationError

from simba.args.toolchain import RawToolchain, Toolchain, ToolchainMatrix


class RawCommonArgs(BaseModel):
    verilator_path: Path
    toolchain_base: RawToolchain = RawToolchain()
    toolchain_extra: List[RawToolchain] = []
    is_verbose: bool = False

    @classmethod
    def resolve_path(cls) -> Path:
        return Path("./.simba.json")

    @classmethod
    def read_json(cls, path: Path) -> "RawCommonArgs":
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
                return cls.model_validate_json(data)
        except ValidationError as e:
            message = ", ".join(
                [f'{err["loc"][0]} {err["type"]}' for err in e.errors()]
            )
            raise ValueError(f"failed to parse config: {message}") from e
        except Exception as e:
            raise RuntimeError(f"failed to read config: {e}") from e


class CommonArgs(NamedTuple):
    verilator_path: Path
    toolchains: ToolchainMatrix
    is_verbose: bool

    @classmethod
    def from_raw(cls, raw: RawCommonArgs) -> "CommonArgs":
        toolchains = []

        if raw.toolchain_extra is None or len(raw.toolchain_extra) == 0:
            raw.toolchain_extra = [raw.toolchain_base]

        for i, extra in enumerate(raw.toolchain_extra or []):
            toolchain = extra | (raw.toolchain_base or RawToolchain())
            try:
                toolchains.append(Toolchain.from_raw(toolchain))
            except ValueError as e:
                raise ValueError(f"bad {i}th toolchain: {e}") from e

        return CommonArgs(
            verilator_path=raw.verilator_path,
            toolchains=toolchains,
            is_verbose=raw.is_verbose,
        )
