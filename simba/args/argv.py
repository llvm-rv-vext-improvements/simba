import argparse
from enum import Enum
from pathlib import Path
from typing import Any, List, NamedTuple

from simba.args.common import RawCommonArgs, CommonArgs


class RunKind(Enum):
    EXECUTABLE = "executable"
    SOURCES = "sources"
    MINIPROJECT = "miniproject"
    SUITE = "suite"


class RunExecutableArgs(NamedTuple):
    path: Path


class RunSourcesArgs(NamedTuple):
    paths: List[Path]


class RunMiniprojectArgs(NamedTuple):
    path: Path


class RunSuiteArgs(NamedTuple):
    path: Path


class TArgs[T](NamedTuple):
    common: CommonArgs
    run: T


class Args(NamedTuple):
    common: CommonArgs
    run: RunExecutableArgs | RunSourcesArgs | RunMiniprojectArgs | RunSuiteArgs

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

        args = parser.parse_args()

        common_args = RawCommonArgs.read_json(RawCommonArgs.resolve_path())
        if args.verbose:
            common_args.is_verbose = True
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

            return Args(
                common=common,
                run=run,
            )
        elif args.command is None:
            raise ValueError(f"command expected, got nothing")
        else:
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
        )

    @classmethod
    def __parse_run_miniproject(cls, args: Any) -> RunMiniprojectArgs:
        if len(args.paths) != 1:
            raise ValueError(
                f"expected a single miniproject, but got {', '.join(args.paths)}"
            )

        return RunMiniprojectArgs(
            path=Path(args.paths[0]),
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
