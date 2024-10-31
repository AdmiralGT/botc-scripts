import json as js
import os
import pytest
from scripts.script_json import get_similarity

current_dir = os.path.dirname(os.path.realpath(__file__))

@pytest.mark.parametrize("orig, new", [
    ("input/trouble_brewing.json", "input/trouble_brewing.json"),
    ("input/trouble_brewing_with_meta.json", "input/trouble_brewing.json"),
    ("input/trouble_brewing.json", "input/trouble_brewing_with_meta.json"),
    ("input/trouble_brewing_with_meta.json", "input/trouble_brewing_with_meta.json"),
])
def test_same(orig, new):
    with open(os.path.join(current_dir, orig), "r") as f:
        v1 = js.load(f)
    with open(os.path.join(current_dir, new), "r") as f:
        v2 = js.load(f)
    similarity = get_similarity(v1, v2, True)
    assert similarity == 100

@pytest.mark.parametrize("orig, new", [
    ("input/trouble_brewing.json", "input/strings_pulling.json"),
    ("input/trouble_brewing_with_meta.json", "input/strings_pulling.json"),
    ("input/trouble_brewing.json", "input/strings_pulling_with_meta.json"),
    ("input/trouble_brewing_with_meta.json", "input/strings_pulling_with_meta.json"),

])
def test_minimal_diff(orig, new):
    with open(os.path.join(current_dir, orig), "r") as f:
        v1 = js.load(f)
    with open(os.path.join(current_dir, new), "r") as f:
        v2 = js.load(f)
    similarity = get_similarity(v1, v2, True)
    # TB has 22 characters, Strings Pulling has 23 characters, 22 of which are on TB
    # 96 = 22/23
    assert similarity == 96
    similarity = get_similarity(v1, v2, False)
    assert similarity == 100
    reverse = get_similarity(v2, v1, True)
    assert reverse == 96
    reverse = get_similarity(v2, v1, False)
    assert reverse == 100


def test_two_changes():
    with open(os.path.join(current_dir, "input/trouble_brewing.json"), "r") as f:
        v1 = js.load(f)
    with open(os.path.join(current_dir, "input/half_of_the_108.json"), "r") as f:
        v2 = js.load(f)
    similarity = get_similarity(v1, v2, True)
    assert similarity == 92
    similarity = get_similarity(v1, v2, False)
    assert similarity == 100
    reverse = get_similarity(v2, v1, True)
    assert reverse == 92
    reverse = get_similarity(v2, v1, False)
    assert reverse == 100

def test_differences_both_ways():
    with open(os.path.join(current_dir, "input/trouble_brewing.json"), "r") as f:
        v1 = js.load(f)
    with open(os.path.join(current_dir, "input/pies_baking.json"), "r") as f:
        v2 = js.load(f)
    similarity = get_similarity(v1, v2, True)
    # 20 out of 23 characters are shared
    assert similarity == 87
    # 20 out of 22 characters are shared
    similarity = get_similarity(v1, v2, False)
    assert similarity == 91
    reverse = get_similarity(v2, v1, True)
    assert reverse == 87
    reverse = get_similarity(v2, v1, False)
    assert reverse == 91
