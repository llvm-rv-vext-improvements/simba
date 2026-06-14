import argparse
from enum import Enum
from pathlib import Path
from typing import Any, List, NamedTuple

from simba.args.common import CommonArgs, RawCommonArgs
from simba.args.input_data import RawInputDataConfig, InputDataConfig


class RunKind(Enum):
    EXECUTABLE = "executable"
    SOURCES = "sources"
    MINIPROJECT = "miniproject"
    SUITE = "suite"


class FormatKind(Enum):
    JSON = "json"
    CSV = "csv"
    HTML = "html"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"{value} is not a valid {cls.__name__}")


class RunExecutableArgs(NamedTuple):
    path: Path


class RunSourcesArgs(NamedTuple):
    paths: List[Path]
    input_data_config: InputDataConfig | None


class RunMiniprojectArgs(NamedTuple):
    path: Path
    input_data_config: InputDataConfig | None


class RunSuiteArgs(NamedTuple):
    path: Path


class ConvertArgs(NamedTuple):
    format: FormatKind


class TArgs[T](NamedTuple):
    common: CommonArgs
    run: T


class Args(NamedTuple):
    common: CommonArgs
    action: (
        RunExecutableArgs
        | RunSourcesArgs
        | RunMiniprojectArgs
        | RunSuiteArgs
        | ConvertArgs
    )

    @classmethod
    def from_argv(cls) -> "Args":
        parser = argparse.ArgumentParser(
            prog="simba",
            description="Simulator Benchmarking Tool",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            required=False,
            action="store_true",
            help="Enable detailed logging",
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        run_parser = subparsers.add_parser("run", help="Run benchmarks")
        run_parser.add_argument(
            "kind",
            choices=[kind.value for kind in RunKind],
            help="Kind of run",
        )
        run_parser.add_argument(
            "paths",
            nargs="+",
            help="Paths to source files or directories",
        )
        run_parser.add_argument(
            "--input-config-path",
            default=None,
            required=False,
            help="Path to input config file for tests",
        )
        run_parser.add_argument(
            "--show-generated-benchmark",
            default=False,
            required=False,
            action="store_true",
            help="Outputs each generated benchmark to stdin",
        )

        convert_parser = subparsers.add_parser(
            "convert",
            help="Convert benchmarking report",
        )
        convert_parser.add_argument(
            "output",
            choices=[kind.value for kind in FormatKind],
            help="Output format",
        )

        args = parser.parse_args()

        common_args = RawCommonArgs.read_json(RawCommonArgs.resolve_path())
        if args.verbose:
            common_args.is_verbose = True
        if hasattr(args, "show_generated_benchmark") and args.show_generated_benchmark:
            common_args.show_benchmark = True
        common = CommonArgs.from_raw(common_args)

        if args.command == "run":
            run: RunExecutableArgs | RunSourcesArgs | RunMiniprojectArgs | RunSuiteArgs
            if args.kind == RunKind.EXECUTABLE.value:
                run = cls.__parse_run_executable(args)
            elif args.kind == RunKind.SOURCES.value:
                run = cls.__parse_run_sources(args)
            elif args.kind == RunKind.MINIPROJECT.value:
                run = cls.__parse_run_miniproject(args)
            elif args.kind == RunKind.SUITE.value:
                run = cls.__parse_run_suite(args)
            else:
                raise ValueError(f"unexpected run kind '{args.kind}'")

            return Args(common=common, action=run)

        if args.command == "convert":
            return Args(
                common=common,
                action=ConvertArgs(
                    format=FormatKind.from_value(args.output),
                ),
            )

        if args.command is None:
            raise ValueError("command expected, got nothing")

        raise ValueError(f"unexpected command '{args.command}'")

    @classmethod
    def __parse_run_executable(cls, args: Any) -> RunExecutableArgs:
        if len(args.paths) != 1:
            raise ValueError(
                f"expected a single executable, but got {', '.join(args.paths)}"
            )

        return RunExecutableArgs(
            path=Path(args.paths[0]),
        )

    @classmethod
    def __parse_run_sources(cls, args: Any) -> RunSourcesArgs:
        return RunSourcesArgs(
            paths=[Path(x) for x in args.paths],
            input_data_config=cls.__get_input_config(args),
        )

    @classmethod
    def __parse_run_miniproject(cls, args: Any) -> RunMiniprojectArgs:
        if len(args.paths) != 1:
            raise ValueError(
                f"expected a single miniproject, but got {', '.join(args.paths)}"
            )

        return RunMiniprojectArgs(
            path=Path(args.paths[0]), input_data_config=cls.__get_input_config(args)
        )

    @classmethod
    def __parse_run_suite(cls, args: Any) -> RunSuiteArgs:
        if len(args.paths) != 1:
            raise ValueError(
                f"expected a single suite, but got {', '.join(args.paths)}"
            )

        return RunSuiteArgs(
            path=Path(args.paths[0]),
        )

    @staticmethod
    def __get_input_config(args: Any) -> InputDataConfig | None:
        if args.input_config_path is None:
            return None

        return InputDataConfig.from_raw(
            RawInputDataConfig.read_json(Path(args.input_config_path))
        )
