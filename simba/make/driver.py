from typing import List, NamedTuple

from simba.args.benchmark_input import BenchmarkVar

DO_NOT_OPTIMIZE_MACRO = (
    '#define DO_NOT_OPTIMIZE(var) asm volatile("" : "+r,m"(var) : : "memory")'
)

TEMPLATE = """//includes
    {includes}
    {do_not_optimize}
    // extern functions
    {extern_decls}
    // ==========
    int main() {{
        // loop
        {loops}
    }}
    """


STUB_FUNCTION = (
    "__attribute__((noinline)) __attribute__((noipa))\n"
    "{return_type} {name}({params}) {{}}\n"
)

STUB_INCLUDES = "#include <stdbool.h>\n#include <stdint.h>\n#include <stddef.h>\n"

INCLUDE = '#include "{}"\n'

FUNCTION_CALL = "{}({});"

EXTERN_FUNCTION = "extern __attribute__((noinline)) __attribute__((noipa)) {} {}({});"
ARG_TEMPLATE = "{} {}"


def get_includes(input_filenames: list[str]) -> str:
    return "".join(INCLUDE.format(file) for file in input_filenames)


def get_function_call(function_name: str, variables: list[str]) -> str:
    return FUNCTION_CALL.format(function_name, ",".join(variables))


def get_extern_function(
    function_name: str,
    function_return_type: str,
    variables: list[tuple[str, str]],
) -> str:
    args = []
    for var_, type_ in variables:
        args.append(ARG_TEMPLATE.format(type_, var_))
    return EXTERN_FUNCTION.format(function_return_type, function_name, ",".join(args))


def get_call_block(function_call_str: str, var_names: list[str]) -> str:
    parts = []
    parts += [f"DO_NOT_OPTIMIZE({var});" for var in var_names]
    parts.append(function_call_str)
    parts += [f"DO_NOT_OPTIMIZE({var});" for var in var_names]
    return "\n        ".join(parts)


def get_paired_call_block(
    prefix_call_str: str, main_call_str: str, var_names: list[str]
) -> str:
    parts = []
    parts += [f"DO_NOT_OPTIMIZE({var});" for var in var_names]
    parts.append(prefix_call_str)
    parts.append(main_call_str)
    parts += [f"DO_NOT_OPTIMIZE({var});" for var in var_names]
    return "\n        ".join(parts)


def get_loops(
    warmup_call_str: str,
    main_call_str: str,
    warmup_iterations: int | None,
    main_iterations: int | None,
) -> str:
    sep = "\n        "
    result = ""

    if warmup_iterations is not None and warmup_iterations != 0:
        copies = sep.join([warmup_call_str] * warmup_iterations)
        result += f"\n        // Warmup iterations\n        {copies}\n    "

    if main_iterations is not None and main_iterations != 0:
        copies = sep.join([main_call_str] * main_iterations)
        result += f"\n        // Bench iterations\n        {copies}\n    "

    return result


class GenerationOptions(NamedTuple):
    variables: list[tuple[str, str]]
    input_filenames: list[str]
    warmup_iterations: int = 0
    main_iterations: int = 0
    prefix_function_name: str | None = None
    is_adjustment: bool = False

    @staticmethod
    def from_variables(
        variables: List[BenchmarkVar],
        warmup_iterations: int = 0,
        main_iterations: int = 0,
        prefix_function_name: str | None = None,
        is_adjustment: bool = False,
    ) -> "GenerationOptions":
        new_vars = []
        new_input_files = set()

        for var_ in variables:
            new_vars.append((var_.variable, var_.var_type))
            new_input_files.add(var_.input_path.name)

        return GenerationOptions(
            variables=new_vars,
            input_filenames=list(new_input_files),
            warmup_iterations=warmup_iterations,
            main_iterations=main_iterations,
            prefix_function_name=prefix_function_name,
            is_adjustment=is_adjustment,
        )


def generate_stub(
    function_name: str,
    function_return_type: str,
    variables: list[tuple[str, str]],
) -> str:
    stub_name = f"simba_stub_{function_name}"
    params = ", ".join(f"{type_} {var_}" for var_, type_ in variables) or "void"
    body = STUB_FUNCTION.format(
        return_type=function_return_type, name=stub_name, params=params
    )
    return f"{STUB_INCLUDES}\n{body}"


def generate_program(
    function_name: str,
    options: GenerationOptions,
    function_return_type: str = "void",
) -> str:
    includes = get_includes(options.input_filenames)
    var_names = [var_ for (var_, _) in options.variables]

    assert options.prefix_function_name
    stub_name = options.prefix_function_name

    extern_prefix = get_extern_function(
        stub_name, function_return_type, options.variables
    )
    extern_main = get_extern_function(
        function_name, function_return_type, options.variables
    )
    extern_decls = f"{extern_prefix}\n    {extern_main}"

    warmup_str = get_paired_call_block(
        get_function_call(stub_name, var_names),
        get_function_call(function_name, var_names),
        var_names,
    )

    main_str = get_paired_call_block(
        get_function_call(options.prefix_function_name, var_names),
        get_function_call(
            function_name if not options.is_adjustment else stub_name, var_names
        ),
        var_names,
    )

    do_not_optimize = DO_NOT_OPTIMIZE_MACRO if var_names else ""

    loops = get_loops(
        warmup_str, main_str, options.warmup_iterations, options.main_iterations
    )

    return TEMPLATE.format(
        includes=includes,
        do_not_optimize=do_not_optimize,
        extern_decls=extern_decls,
        loops=loops,
    )
