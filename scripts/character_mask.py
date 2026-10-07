from django.db.models import Func, IntegerField

MASK_BITS = 512


class BitAnd(Func):
    arg_joiner = " & "
    template = "(%(expressions)s)"


class BitCount(Func):
    function = "bit_count"
    output_field = IntegerField()


def build_mask(content: list, bit_map: dict[str, int]) -> str:
    bits = ["0"] * MASK_BITS
    for item in content:
        character_id = item.get("id") if isinstance(item, dict) else item
        index = bit_map.get(character_id) if isinstance(character_id, str) else None
        if index is not None:
            bits[index] = "1"
    return "".join(bits)
