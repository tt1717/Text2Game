from django import template

register = template.Library()

PIECE_TO_CHAR = {
    1: "ひ", 2: "キ", 3: "ゾ", 4: "ラ", 5: "に",
    -1: "ひ", -2: "キ", -3: "ゾ", -4: "ラ", -5: "に", 0: ""
}

@register.filter
def piece_to_char(value):
    return PIECE_TO_CHAR.get(value, "") 