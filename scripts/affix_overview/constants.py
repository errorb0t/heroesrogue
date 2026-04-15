from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = PACKAGE_DIR / "config"
MOD_ROOT = ROOT / "mods" / "HeroesRogue.StormMod"
TEXTURES_DIR = MOD_ROOT / "Base.StormAssets" / "Assets" / "Textures"
AFFIX_DATA_PATH = MOD_ROOT / "Base.StormData" / "GameData" / "AffixData.xml"
LIB_AFFX_SOURCE_PATH = MOD_ROOT / "Base.StormData" / "LibAffx.galaxy"
LIB_AFFX_HEADER_PATH = MOD_ROOT / "Base.StormData" / "LibAffx_h.galaxy"
AFFIX_TRIGGERS_PATH = MOD_ROOT / "Base.StormData" / "AffixTriggers.galaxy"
GAME_DATA_DIR = MOD_ROOT / "Base.StormData" / "GameData"
STRINGS_PATH = MOD_ROOT / "enUS.StormData" / "LocalizedData" / "GameStrings.txt"
DYNAMIC_OVERRIDES_PATH = CONFIG_DIR / "dynamic_overrides.json"
HERO_NAME_OVERRIDES_PATH = CONFIG_DIR / "hero_names.json"
MAP_NAME_OVERRIDES_PATH = CONFIG_DIR / "map_names.json"

RARITY_ORDER = ["Starter", "Common", "Uncommon", "Rare", "Epic", "Legendary"]
RARITY_FILTERS = [
    ("all", "All"),
    ("hero-limited", "Hero-specific"),
    *((rarity, rarity) for rarity in RARITY_ORDER),
]
RARITY_COLORS = {
    "Starter": "#e6cc80",
    "Common": "#f2f5f8",
    "Uncommon": "#3de26d",
    "Rare": "#4f95ff",
    "Epic": "#d26dff",
    "Legendary": "#ff9d3a",
}
STORM_COLORS = {
    "#TooltipNumbers": "#ffd96a",
    "#TooltipQuest": "#99d0ff",
}
FIELD_VALUE_ATTRIBUTES = ("String", "Int", "value", "Value")
HERO_TAG_LABELS = {
    "mana": "Mana heroes only",
    "!mana": "Non-mana heroes only",
    "melee": "Melee heroes only",
    "!melee": "Non-melee heroes only",
    "ranged": "Ranged heroes only",
    "!ranged": "Non-ranged heroes only",
    "all": "All heroes",
    "!all": "No heroes",
    "starter": "Starter heroes only",
    "!starter": "Non-starter heroes only",
}
GITHUB_URL = "https://github.com/sobbyellow/heroesrogue"
NAV_ITEMS = [
    ("index.html", "Boons", "boons"),
    ("curses.html", "Curses", "curses"),
    ("difficulties.html", "Difficulties", "difficulties"),
]
FOOTER_NOTE = (
    "This Compendium is generated programmatically and may contain errors. "
    "Heroes Rogue is a fan-made project and is not affiliated with or endorsed "
    "by Blizzard Entertainment. The mod runs locally and does not interact with "
    "Blizzard's servers. All original game assets, characters, and intellectual "
    "property belong to Blizzard Entertainment."
)
