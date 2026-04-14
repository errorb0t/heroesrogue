from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AffixRecord:
    affix_id: str
    name: str
    tooltip_html: str
    tooltip_plain: str
    rarity: str
    icon_name: str
    icon_url: str
    negative: bool
    hero_specific: str
    hero_specific_raw: str
    uses_placeholder: bool


@dataclass
class DifficultyRecord:
    difficulty_value: int
    label: str
    localized_name_key: str
    localized_tooltip_key: str
    tooltip_html: str
    tooltip_plain: str
