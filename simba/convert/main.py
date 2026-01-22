import sys

from simba.args.argv import ConvertArgs, FormatKind
from simba.convert.csv import reports_to_table, table_to_csv, table_to_diff
from simba.convert.html import table_to_html
from simba.convert.json import reports_from_json


def run_convert(args: ConvertArgs):
    content = sys.stdin.read()
    reports = reports_from_json(content)

    if args.format == FormatKind.JSON:
        print(content)
    elif args.format == FormatKind.CSV:
        table = table_to_diff(reports_to_table(reports))
        print(table_to_csv(table))
    elif args.format == FormatKind.HTML:
        table = table_to_diff(reports_to_table(reports))
        print(table_to_html(table))
    else:
        raise RuntimeError(f"unexpected format: {args.format}")
