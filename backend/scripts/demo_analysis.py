from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.demo_data import build_demo_analysis


def main() -> None:
    analysis, _events = build_demo_analysis()
    payload = {
        "region_id": analysis.region.region_id,
        "status": analysis.result.status.value,
        "summary": analysis.region.summary.model_dump(),
        "ranking_formula": "final_rank_score = severity_score * confidence_score after anomaly gate",
        "top_hotspots": [item.model_dump(mode="json") for item in analysis.result.top_hotspots],
        "discarded_hotspot_ids": analysis.result.discarded_hotspot_ids,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
