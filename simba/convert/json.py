import json
from typing import Any, Dict, List

from pydantic import TypeAdapter

from simba.run.report import RawReport, Report


def reports_to_dict(reports: List[Report]) -> List[Dict[str, Any]]:
    return [RawReport.from_pure(report).model_dump() for report in reports]


def reports_to_json(reports: List[Report]) -> str:
    return json.dumps(
        reports_to_dict(reports),
        indent=4,
        sort_keys=True,
    )


def reports_from_json(content: str) -> List[Report]:
    raws = TypeAdapter(List[RawReport]).validate_json(content)
    return [raw.to_pure() for raw in raws]
