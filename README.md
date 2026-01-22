# SimBa

SimBa (Simulator Benchmarking) is a tool to easily get performance metrics
of a source code (C and LLVM IR), compiled by a given compiler, configured
by a given compilation flags, ran on a XiangShan (RISC-V) Verilator simulator.

SimBa focuses on user-friendliness for a daily usage, but also can be used at
CI/CD pipelines.

## Functionality

1. Running a bare metal executable on a given Verilator simulator.

```sh
simba run executable ./a.out
```

2. "Running" C and LLVM IR sources into a bare metal binary.

```sh
simba run miniproject ./main.c ./lib.ll
simba run miniproject ./sample/
```

3. Output performance metrics such as instructions and cycles count
   in various formats.

```sh
simba run miniproject ./hello/main.c --name=hello --output-format=json
# {
#   "name": "hello",
#   "instructions": 1999,
#   "cycles": 19858
# }
```

4. Configuration via a JSON file with an extension by ARGV.

```sh
simba run ... --config-path=/home/xxx/.simba.json

simba conf path
# /home/xxx/.simba.json

cat /home/xxx/.simba.json
# {
#     "verilator_path": "/home/xxx/emu",
#     "output_format": "json",
#     "toolchain_base": {
#        "path": "/usr/lib/llvm-18",
#        "cflags": "A B C"
#     },
#     "toolchain_matrix": [
#         {
#           "cflags": "D E F"
#         },
#     ]
# }
```

5. "Running" an entire miniproject suite.

```sh
simba run suite ./suites --output-format=json
# [
#   {
#     "name": "hello",
#     "instructions": 1999,
#     "cycles": 19858
#   },
#     "name": "goodbye",
#     "instructions": 5131,
#     "cycles": 78126
#   },
# ]
```

6. "Running" with a configuration matrix.

7. Visualizing benchmarking results via a Web page.
