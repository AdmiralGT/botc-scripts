import json as js
import os
import pytest
from scripts.script_json import get_json_additions

current_dir = os.path.dirname(os.path.realpath(__file__))

@pytest.mark.parametrize("orig, new", [
    ("input/trouble_brewing.json", "input/strings_pulling.json"),
    ("input/trouble_brewing.json", "input/strings_pulling_with_meta.json"),
    ("input/trouble_brewing_with_meta.json", "input/strings_pulling.json"),
    ("input/trouble_brewing_with_meta.json", "input/strings_pulling_with_meta.json"),

])
def test_one_addition(orig, new):
    with open(os.path.join(current_dir, orig), "r") as f:
        v1 = js.load(f)
    with open(os.path.join(current_dir, new), "r") as f:
        v2 = js.load(f)
    addition = get_json_additions(v1.copy(), v2.copy())
    assert addition == [{"id": "marionette"}]
    reverse = get_json_additions(v2, v1)
    assert reverse == []


def test_two_additions():
    with open(os.path.join(current_dir, "input/trouble_brewing.json"), "r") as f:
        v1 = js.load(f)
    with open(os.path.join(current_dir, "input/half_of_the_108.json"), "r") as f:
        v2 = js.load(f)
    addition = get_json_additions(v1.copy(), v2.copy())
    assert addition == [{"id": "legion"},{"id": "vortox"}]
    reverse = get_json_additions(v2, v1)
    assert reverse == []


def test_additions_and_removals():
    with open(os.path.join(current_dir, "input/trouble_brewing.json"), "r") as f:
        v1 = js.load(f)
    with open(os.path.join(current_dir, "input/pies_baking.json"), "r") as f:
        v2 = js.load(f)
    addition = get_json_additions(v1.copy(), v2.copy())
    assert addition == [{"id": "noble"},{"id": "cannibal"},{"id": "marionette"}]
    reverse = get_json_additions(v2, v1)
    assert reverse == [{"id": "investigator"},{"id": "undertaker"}]
