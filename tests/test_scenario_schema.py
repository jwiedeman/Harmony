import pytest
from pydantic import ValidationError

from backend.scenarios import Scenario


def test_parse_example_scenario():
    data = {
        "name": "VOD with preroll + midroll + pause + buffer",
        "streamType": "vod",
        "expect": [
            {"type": "sessionStart"},
            {"type": "play", "after": "sessionStart"},
        ],
        "constraints": {
            "mainPing": {"cadenceSec": 10, "toleranceSec": 2},
            "livePlayheadMode": False,
        },
        "paramRules": [
            {"on": "All", "require": ["s:sc:rsid"]}
        ],
    }
    scenario = Scenario.model_validate(data)
    assert scenario.name.startswith("VOD")
    assert scenario.expect[0].type == "sessionStart"
    assert scenario.constraints.mainPing.cadenceSec == 10
    assert scenario.paramRules[0].require == ["s:sc:rsid"]


def test_expect_required():
    with pytest.raises(ValidationError):
        Scenario.model_validate({"name": "missing"})
