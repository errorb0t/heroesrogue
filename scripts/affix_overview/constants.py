from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MOD_ROOT = ROOT / "mods" / "HeroesRogue.StormMod"
TEXTURES_DIR = MOD_ROOT / "Base.StormAssets" / "Assets" / "Textures"
AFFIX_DATA_PATH = MOD_ROOT / "Base.StormData" / "GameData" / "AffixData.xml"
LIB_AFFX_SOURCE_PATH = MOD_ROOT / "Base.StormData" / "LibAffx.galaxy"
LIB_AFFX_HEADER_PATH = MOD_ROOT / "Base.StormData" / "LibAffx_h.galaxy"
AFFIX_TRIGGERS_PATH = MOD_ROOT / "Base.StormData" / "AffixTriggers.galaxy"
GAME_DATA_DIR = MOD_ROOT / "Base.StormData" / "GameData"
STRINGS_PATH = MOD_ROOT / "enUS.StormData" / "LocalizedData" / "GameStrings.txt"
DYNAMIC_OVERRIDES_PATH = ROOT / "scripts" / "affix_dynamic_overrides.json"
HERO_NAME_OVERRIDES_PATH = ROOT / "scripts" / "affix_hero_names.json"

RARITY_ORDER = ["Starter", "Common", "Uncommon", "Rare", "Epic", "Legendary"]
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
