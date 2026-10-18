import json as js
import os

import pytest

from scripts.character_mask import MASK_BITS, build_mask

current_dir = os.path.dirname(os.path.realpath(__file__))


def load(name):
    with open(os.path.join(current_dir, "input", name), "r") as f:
        return js.load(f)


def character_ids(*names):
    return {item["id"] for name in names for item in load(name) if item.get("id") != "_meta"}


SCRIPTS = ("trouble_brewing.json", "strings_pulling.json", "half_of_the_108.json", "pies_baking.json")
BIT_MAP = {character_id: index for index, character_id in enumerate(sorted(character_ids(*SCRIPTS)))}


def mask(content):
    return int(build_mask(content, BIT_MAP), 2)


def test_mask_length_and_bits():
    tb = load("trouble_brewing.json")
    result = build_mask(tb, BIT_MAP)
    assert len(result) == MASK_BITS
    assert result.count("1") == 22
    assert result[BIT_MAP["washerwoman"]] == "1"
    assert result[BIT_MAP["marionette"]] == "0"


@pytest.mark.parametrize("name", ["trouble_brewing.json", "strings_pulling.json"])
def test_meta_ignored(name):
    content = load(name)
    meta = {"id": "_meta", "name": "Test"}
    assert mask([meta, *content]) == mask([*content, meta]) == mask(content)


def test_unknown_and_string_entries():
    content = ["washerwoman", {"id": "unknown"}, {"name": "no id"}, 5, {"id": ["list"]}]
    assert build_mask(content, BIT_MAP).count("1") == 1


def test_subset():
    tb = mask(load("trouble_brewing.json"))
    sp = mask(load("strings_pulling.json"))
    assert tb & sp == tb
    assert (tb & sp).bit_count() == 22
    assert sp.bit_count() == 23


def test_partial_overlap():
    tb = mask(load("trouble_brewing.json"))
    pies = mask(load("pies_baking.json"))
    shared = tb & pies
    assert shared != tb
    assert shared != pies
    assert 0 < shared.bit_count() < 22
