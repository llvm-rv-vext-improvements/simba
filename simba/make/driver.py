from typing import Self, List

from simba.args.input_data import BenchmarkVar

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
    main_iterations: int | None,
) -> str:
    if warmup_iterations is None and main_iterations is None:
        return WITHOUT_LOOP.format(function_call_str)

    loop_str = ""
    if warmup_iterations is not None:
        loop_str += WARMUP_LOOP.format(warmup_iterations, function_call_str)
    if main_iterations is not None:
        loop_str += BENCH_LOOP.format(main_iterations, function_call_str)
    return loop_str


class GenerationOptions:

    def __init__(
        self,
        variables: list[tuple[str, str]] | None = None,
        input_filenames: list[str] | None = None,
        warmup_iterations: int | None = None,
        main_iterations: int | None = None,
    ):
        self.variables = variables
        self.input_filenames = input_filenames
        self.warmup_iterations = warmup_iterations
        self.main_iterations = main_iterations

    def set_warmup_iterations(self, iterations: int) -> Self:
        self.warmup_iterations = iterations
        return self

    def set_main_iterations(self, iterations: int) -> Self:
        self.main_iterations = iterations
        return self

    @staticmethod
    def from_variables(variables: List[BenchmarkVar]) -> "GenerationOptions":
        new_vars = []
        new_input_files = set()

        for var_ in variables:
            new_vars.append((var_.variable, var_.type_))
            new_input_files.add(var_.input_path.name)

        return GenerationOptions(
            variables=new_vars, input_filenames=list(new_input_files)
        )


def generate_program(
    function_name: str,
    options: GenerationOptions,
    function_return_type: str = "void",
) -> str:
    includes = get_includes(options.input_filenames)
    extern_func_str = get_extern_function(
        function_name, function_return_type, options.variables
    )
    function_call_str = get_function_call(
        function_name, [var_ for (var_, _) in options.variables or []]
    )
    loops = get_loops(
        function_call_str,
        options.warmup_iterations,
        options.benchmark_iterations,
    )

    return TEMPLATE.format(
        includes,
        extern_func_str,
        loops,
    )
