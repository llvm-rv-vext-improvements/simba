import logging
import sys

loggy = logging.getLogger("simba")
loggy.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("%(message)s"))

loggy.addHandler(handler)
loggy.propagate = False
