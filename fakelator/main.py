#!/usr/bin/env python3
"""Fake XiangShan verilator simulator for testing."""

import argparse
import os
import random
import sys


def emit_happy_stdout(executable_path: str) -> None:
    instr_cnt = random.randint(10, 1000)
    cycle_cnt = random.randint(5000, 15000)
    ipc = instr_cnt / cycle_cnt
    host_time_ms = random.randint(60000, 90000)
    loading_bytes = random.randint(100, 500)
    pc = random.randint(0x80000010, 0x80000100)

    print("# xiangshan compiled at Jan  1 1980, 00:00:00")
    print(
        "# [WARNING] /home/khaser/llvm-project/cpu-rtl/build/constantin.txt"
        " does not exist, so all constants default to initialized values."
    )
    print("# Using simulated 32768B flash")
    print("# Core  0's Commit SHA is: 1f3fb10e4e, dirty: 0")
    print("# Using simulated 8386560MB RAM")
    print(f"# The image is {executable_path}")
    print("# ELF file detected and loading image from extracted elf file")
    print(f"# Loading {loading_bytes} bytes at address 0x80000000 at offset 0x0")
    print(f"# Core 0: HIT GOOD TRAP at pc = 0x{pc:08x}")
    print(
        f"# Core-0 instrCnt = {instr_cnt},"
        f" cycleCnt = {cycle_cnt},"
        f" IPC = {ipc:.6f}"
    )
    print(
        f"# Seed=0 Guest cycle spent: {cycle_cnt + random.randint(1, 10)}"
        " (this will be different from cycleCnt if emu loads a snapshot)"
    )
    print(f"# Host time spent: {host_time_ms}ms")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fake XiangShan verilator simulator")
    parser.add_argument("--no-diff", action="store_true")
    parser.add_argument("-i", dest="executable", required=True, metavar="PATH")
    parser.add_argument("--sad", action="store_true", help="Simulate a failure")
    args = parser.parse_args()

    sad = args.sad or os.environ.get("FAKELATOR_SAD", "0") == "1"

    if sad:
        print("FATAL: simulation failed", file=sys.stderr)
        sys.exit(1)

    emit_happy_stdout(args.executable)


if __name__ == "__main__":
    main()
