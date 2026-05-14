TEMPLATE = """//includes
    {}
    // extern function
    {}
    // ==========
    int main() {{
        // loop
        {}
    }}
    """


WARMUP_LOOP = """
        // Warmup iterations
        for (int i = 0; i < {}; i++) {{
            // Function call
            {}
        }}
    """

BENCH_LOOP = """
        // Bench iterations
        for (int i = 0; i < {}; i++) {{
            // Function call
            {}
        }}
    """

WITHOUT_LOOP = "{} // Function call"

INCLUDE = '#include "{}"\n'

FUNCTION_CALL = "{}({});"

EXTERN_FUNCTION = "extern {} {}({});"
ARG_TEMPLATE = "{} {}"


def get_includes(input_filenames: list[str] | None = None) -> str:
    include_str = ""

    for file in input_filenames or []:
        include_str += INCLUDE.format(file)

    return include_str


def get_function_call(function_name: str, variables: list[str] | None) -> str:
    return FUNCTION_CALL.format(function_name, ",".join(variables or []))


def get_extern_function(
    function_name: str,
    function_return_type: str,
    variables: list[tuple[str, str]] | None,
) -> str:
    args = []

    for var_, type_ in variables or []:
        args.append(ARG_TEMPLATE.format(type_, var_))
    return EXTERN_FUNCTION.format(function_return_type, function_name, ",".join(args))


def get_loops(
    function_call_str: str,
    warmup_iterations: int | None,
    benchmark_iterations: int | None,
) -> str:
    if warmup_iterations is None and benchmark_iterations is None:
        return WITHOUT_LOOP.format(function_call_str)

    loop_str = ""
    if warmup_iterations is not None:
        loop_str += WARMUP_LOOP.format(warmup_iterations, function_call_str)
    if benchmark_iterations is not None:
        loop_str += BENCH_LOOP.format(benchmark_iterations, function_call_str)
    return loop_str


def generate_program(
    function_name: str,
    function_return_type: str = "void",
    variables: list[tuple[str, str]] | None = None,
    input_filenames: list[str] | None = None,
    warmup_iterations: int | None = None,
    benchmark_iterations: int | None = None,
) -> str:
    includes = get_includes(input_filenames)
    extern_func_str = get_extern_function(
        function_name, function_return_type, variables
    )
    function_call_str = get_function_call(
        function_name, [var_ for (var_, _) in variables]
    )
    loops = get_loops(
        function_call_str,
        warmup_iterations,
        benchmark_iterations,
    )

    return TEMPLATE.format(
        includes,
        extern_func_str,
        loops,
    )
