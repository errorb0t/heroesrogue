from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AffixCondition:
    key: str
    label: str
    value: str
    search_text: str


@dataclass
class AffixRecord:
    affix_id: str
    name: str
    tooltip_html: str
    tooltip_plain: str
    rarity: str
    max_stacks: int
    icon_name: str
    icon_url: str
    negative: bool
    hero_specific: str
    has_hero_condition: bool
    conditions: list[AffixCondition]
    uses_placeholder: bool


@dataclass
class DifficultyRecord:
    difficulty_value: int
    label: str
    localized_name_key: str
    localized_tooltip_key: str
    tooltip_html: str
    tooltip_plain: str
