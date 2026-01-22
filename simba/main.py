from simba.args.argv import (
    Args,
    ConvertArgs,
)
from simba.convert.main import run_convert
from simba.log import loggy
from simba.run.main import main as run_main


def main():
    try:
        args = Args.from_argv()
        loggy.debug("Parsed %s", args)

        if not isinstance(args.action, ConvertArgs):
            run_main(args)
        elif isinstance(args.action, ConvertArgs):
            run_convert(args.action)
        else:
            raise RuntimeError(f"unexpected type: {type(args.action)}")

    except Exception as e:
        loggy.error(e)

    except KeyboardInterrupt as e:
        loggy.error("Interrupted")


if __name__ == "__main__":
    main()
