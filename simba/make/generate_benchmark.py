
template = (
    """//includes
    {}
    // extern function
    {}
    // ==========
    int main() {{
        // loop
        {}
    }}
    """
)


warmup_loop = (
    """
        // Warmup iterations
        for (int i = 0; i < {}; i++) {{
            // Function call
            {}
        }}
    """
)

bench_loop = (
    """
        // Bench iterations
        for (int i = 0; i < {}; i++) {{
            // Function call
            {}
        }}
    """
)

without_loop = "{} // Function call"

include = '#include "{}"\n'

function_call = "{}({});"

extern_function = "extern {}({});"
arg_template = "{} {}"

def get_includes(input_filenames: list[str] | None = None) -> str:
    include_str = ""

    for file in input_filenames or []:
        include_str += include.format(file)

    return include_str

def get_function_call(function_name: str, variables: list[str] | None) -> str:
    return function_call.format(
        function_name,
        ','.join(variables or [])
    )

def get_extern_function(function_name: str, variables: list[tuple[str, str]] | None) -> str:
    args = []

    for (var_, type_) in variables or []:
        args.append(
            arg_template.format(type_, var_)
        )
    return extern_function.format(
        function_name,
        ','.join(args)
    )

def get_loops(
    function_call_str: str,
    warmup_iterations: int | None,
    benchmark_iterations: int | None
) -> str:
    if warmup_iterations is None and benchmark_iterations is None:
        return without_loop.format(function_call_str)
    
    loop_str = ""
    if warmup_iterations is not None:
        loop_str += warmup_loop.format(warmup_iterations, function_call)
    if benchmark_iterations is not None:
        loop_str += bench_loop.format(benchmark_iterations, function_call)
    return loop_str


def generate_program(
    function_name: str,
    variables: list[tuple[str, str]] | None = None,
    input_filenames: list[str] | None = None,
    warmup_iterations: int | None = None,
    benchmark_iterations: int | None = None,
) -> str:
    includes = get_includes(input_filenames)
    extern_func_str = get_extern_function(function_name, variables)
    function_call_str = get_function_call(
        function_name, [var_ for (var_, _) in variables]
    )
    loops = get_loops(
        function_call_str,
        warmup_iterations,
        benchmark_iterations,
    )

    return template.format(
        includes,
        extern_func_str,
        loops,
    )
