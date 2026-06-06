import html
from datetime import datetime
from typing import Iterable

from simba.convert.csv import DiffBenchmarkRow


def table_to_html(table: Iterable[DiffBenchmarkRow]) -> str:
    table = list(table)
    max_diffs = max((len(row.diffs) for row in table), default=0)

    all_toolchains = set()
    if table:
        for row in table:
            all_toolchains.add(row.base.toolchain)
            for diff in row.diffs:
                all_toolchains.add(diff.toolchain)

    sorted_toolchains = sorted(list(all_toolchains), key=repr)
    toolchain_map = {tc: chr(ord("A") + i) for i, tc in enumerate(sorted_toolchains)}
    letter_map = {v: k for k, v in toolchain_map.items()}

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    toolchain_colors = [
        "#0d6efd",
        "#198754",
        "#ffc107",
        "#dc3545",
        "#6f42c1",
        "#0dcaf0",
        "#d63384",
        "#6c757d",
    ]
    color_css_parts = []
    for i in range(len(sorted_toolchains)):
        letter = chr(ord("A") + i)
        color = toolchain_colors[i % len(toolchain_colors)]
        color_css_parts.append(f".tc-{letter} {{ color: {color}; font-weight: bold; }}")
    color_css = "\n        ".join(color_css_parts)

    # Divider indices (1-indexed for CSS nth-child)
    # New column layout: 1=Name, 2=BenchmarkConfig, 3=Conf0, 4=Instrs0, 5=Cycles0,
    # then for each diff: 6=Conf1,7=Instrs1,8=ΔInstrs1,9=ΔInstrs1',10=Cycles1,11=ΔCycles1,12=ΔCycles1', etc.
    divider_indices = []
    if table:
        divider_indices.append(2)      # after Config column
        divider_indices.append(5)      # after base metrics (Conf0/Instrs0/Cycles0)
        for i in range(1, max_diffs + 1):
            # last column of diff i is at position 5 + i*7
            divider_indices.append(5 + i * 7)

    divider_css = ""
    if divider_indices:
        selectors = ",\n        ".join(
            [f"th:nth-child({i}), td:nth-child({i})" for i in divider_indices]
        )
        divider_css = f"{selectors} {{ border-right: 2px solid #555; }}"

    css = f"""
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 2em; background-color: #fdfdfd; color: #333; }}
        h1, h2 {{ color: #111; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        table {{ border-collapse: collapse; width: auto; margin-bottom: 2em; font-size: 0.9em; }}
        th, td {{ border: 1px solid #ddd; padding: 8px 10px; white-space: nowrap; }}
        td:first-child, th:first-child {{ text-align: left; font-weight: bold; }}
        td:nth-child(2) {{ text-align: left; white-space: normal; max-width: 300px; word-break: break-word; }}  /* config column */
        thead th {{ background-color: #f2f2f2; position: sticky; top: 0; z-index: 10; }}
        tbody tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tbody tr:hover {{ background-color: #e9e9e9; }}
        .positive-diff {{ color: #198754; }}
        .negative-diff {{ color: #dc3545; }}
        .sortable {{ cursor: pointer; user-select: none; }}
        .sortable::after {{ content: " \\2195"; opacity: 0.3; }}
        .sort-asc::after {{ content: " \\25B2"; opacity: 1; }}
        .sort-desc::after {{ content: " \\25BC"; opacity: 1; }}
        .legend-table td:last-child {{ text-align: left; white-space: pre-wrap; word-break: break-all; font-family: monospace; font-weight: normal; }}
        .legend-table td:first-child {{ text-align: center; font-weight: bold; }}
        {color_css}
        {divider_css}
    """

    js = """
        const getCellValue = (tr, idx) => {
            const cell = tr.children[idx];
            if (!cell) return '';
            const val = cell.dataset.sortValue || cell.innerText || cell.textContent;
            return val;
        };

        const isNumeric = (val) => {
            return !isNaN(parseFloat(val)) && isFinite(val);
        };

        const sorter = (idx, asc) => (a, b) => {
            const valA = getCellValue(a, idx).replace(/[+,%]/g, '');
            const valB = getCellValue(b, idx).replace(/[+,%]/g, '');

            if (isNumeric(valA) && isNumeric(valB)) {
                return (parseFloat(valA) - parseFloat(valB)) * (asc ? 1 : -1);
            }

            const strA = String(valA);
            const strB = String(valB);

            return strA.localeCompare(strB, undefined, {numeric: true}) * (asc ? 1 : -1);
        };

        document.addEventListener('DOMContentLoaded', () => {
            document.querySelectorAll('#results-table .sortable').forEach(th => {
                th.addEventListener('click', (() => {
                    const table = th.closest('table');
                    const tbody = table.querySelector('tbody');
                    if (!tbody) return;
                    const thIndex = Array.from(th.parentNode.children).indexOf(th);
                    const currentIsAsc = th.classList.contains('sort-asc');

                    document.querySelectorAll('#results-table .sortable').forEach(h => {
                        h.classList.remove('sort-asc', 'sort-desc');
                    });

                    if (currentIsAsc) {
                        th.classList.add('sort-desc');
                    } else {
                        th.classList.add('sort-asc');
                    }

                    Array.from(tbody.querySelectorAll('tr'))
                        .sort(sorter(thIndex, !currentIsAsc))
                        .forEach(tr => tbody.appendChild(tr));
                }));
            });
        });
    """

    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "<title>SimBa Report</title>",
        f"<style>{css}</style>",
        "</head>",
        "<body>",
        f"<h1>SimBa Report</h1><p>Generated on: {current_time}</p>",
    ]

    html_parts.append("<h2>Toolchain Legend</h2>")
    html_parts.append(
        '<table class="legend-table"><thead><tr><th>ID</th><th>Configuration</th></tr></thead><tbody>'
    )
    for letter, toolchain in sorted(letter_map.items()):
        html_parts.append(
            f'<tr><td class="tc-{letter}">{letter}</td><td>{html.escape(repr(toolchain))}</td></tr>'
        )
    html_parts.append("</tbody></table>")

    html_parts.append("<h2>Benchmark Results</h2>")
    if not table:
        html_parts.append("<p>No benchmark data to display.</p>")
    else:
        html_parts.append('<table id="results-table">')
        html_parts.append("<thead><tr>")

        # Header columns: Name, Config, then base, then diffs
        header_th_parts = [
            '<th class="sortable">Name</th>',
            '<th class="sortable">Benchmark Config</th>',
            '<th class="sortable">Conf<sub>0</sub></th>',
            '<th class="sortable">Instrs<sub>0</sub></th>',
            '<th class="sortable">Cycles<sub>0</sub></th>',
        ]

        for i in range(1, max_diffs + 1):
            header_th_parts.extend(
                [
                    f'<th class="sortable">Conf<sub>{i}</sub></th>',
                    f'<th class="sortable">Instrs<sub>{i}</sub></th>',
                    f'<th class="sortable">&Delta;Instrs<sub>{i}</sub></th>',
                    f'<th class="sortable">&Delta;Instrs<sub>{i}</sub>&apos;</th>',
                    f'<th class="sortable">Cycles<sub>{i}</sub></th>',
                    f'<th class="sortable">&Delta;Cycles<sub>{i}</sub></th>',
                    f'<th class="sortable">&Delta;Cycles<sub>{i}</sub>&apos;</th>',
                ]
            )

        html_parts.append("".join(header_th_parts))
        html_parts.append("</tr></thead>")
        html_parts.append("<tbody>")

        for row in table:
            row_parts = ["<tr>"]
            # Name column with italic if trampolined
            name_cell = f"<i>{html.escape(row.name)}</i>" if row.base.is_customly_trampolined else html.escape(row.name)
            row_parts.append(f"<td>{name_cell}</td>")

            # Config column
            config_str = row.config.to_csv_str() if row.config else ""
            row_parts.append(f"<td>{html.escape(config_str)}</td>")

            # Base toolchain column (Conf0)
            base_letter = toolchain_map.get(row.base.toolchain, "?")
            row_parts.append(f'<td class="tc-{base_letter}">{base_letter}</td>')
            row_parts.append(f"<td>{row.base.instrs:,}</td>")
            row_parts.append(f"<td>{row.base.cycles:,}</td>")

            # Diff columns
            for diff in row.diffs:
                def get_diff_class(val):
                    return "negative-diff" if val > 0 else "positive-diff" if val < 0 else ""

                diff_letter = toolchain_map.get(diff.toolchain, "?")
                row_parts.append(f'<td class="tc-{diff_letter}">{diff_letter}</td>')
                row_parts.append(f"<td>{diff.instrs:,}</td>")
                row_parts.append(f'<td class="{get_diff_class(diff.instrs_diff_abs)}">{diff.instrs_diff_abs:+,}</td>')
                row_parts.append(f'<td class="{get_diff_class(diff.instrs_diff_rel)}" data-sort-value="{diff.instrs_diff_rel}">{diff.instrs_diff_rel:+.2%}</td>')
                row_parts.append(f"<td>{diff.cycles:,}</td>")
                row_parts.append(f'<td class="{get_diff_class(diff.cycles_diff_abs)}">{diff.cycles_diff_abs:+,}</td>')
                row_parts.append(f'<td class="{get_diff_class(diff.cycles_diff_rel)}" data-sort-value="{diff.cycles_diff_rel}">{diff.cycles_diff_rel:+.2%}</td>')

            # Fill missing diff columns if this row has fewer diffs
            missing = max_diffs - len(row.diffs)
            if missing > 0:
                row_parts.append("<td></td>" * (missing * 7))

            row_parts.append("</tr>")
            html_parts.append("".join(row_parts))

        html_parts.append("</tbody></table>")
        html_parts.append(
            "<p><em>Note: Italicized benchmark names indicate custom trampoline configuration.</em></p>"
        )

    html_parts.append(f"<script>{js}</script>")
    html_parts.append("</body></html>")

    return "\n".join(html_parts)