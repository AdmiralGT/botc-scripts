import json as js
import os
import pytest
from scripts.script_json import get_json_changes

current_dir = os.path.dirname(os.path.realpath(__file__))


@pytest.mark.parametrize(
    "orig, new",
    [
        ("input/trouble_brewing.json", "input/strings_pulling.json"),
        ("input/trouble_brewing.json", "input/strings_pulling_with_meta.json"),
        ("input/trouble_brewing_with_meta.json", "input/strings_pulling.json"),
        (
            "input/trouble_brewing_with_meta.json",
            "input/strings_pulling_with_meta.json",
        ),
        ("input/trouble_brewing.json", "input/half_of_the_108.json"),
        ("input/trouble_brewing.json", "input/pies_baking.json"),
    ],
)
def test_clocktower_scripts(orig, new):
    with open(os.path.join(current_dir, orig), "r") as f:
        v1 = js.load(f)
    with open(os.path.join(current_dir, new), "r") as f:
        v2 = js.load(f)
    changes = get_json_changes(v1.copy(), v2.copy())
    assert changes == []


def test_homebrew():
    with open(os.path.join(current_dir, "input/hybrid1.json"), "r") as f:
        v1 = js.load(f)
    with open(os.path.join(current_dir, "input/hybrid2.json"), "r") as f:
        v2 = js.load(f)
    changes = get_json_changes(v1.copy(), v2.copy())
    assert changes == [{"id": "custom_imp"}]
