from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Mapping

from .constants import (
    AFFIX_DATA_PATH,
    LIB_AFFX_SOURCE_PATH,
    RARITY_ORDER,
)
from .dynamic_values import DynamicValueResolver
from .markup import convert_storm_markup
from .models import AffixRecord, DifficultyRecord


def load_strings(path: Path) -> dict[str, str]:
    strings: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if "=" not in line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        strings[key.strip()] = value
    return strings


def load_mod_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'const string libAffx_version = "([^"]+)";', text)
    if match is None:
        raise RuntimeError(f"Unable to find libAffx_version in {path}")
    return match.group(1)


def load_dynamic_value_overrides(
    path: Path, inline_overrides: list[str]
) -> dict[str, float]:
    overrides: dict[str, float] = {}

    if path.exists():
        raw_data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw_data, dict):
            raise RuntimeError(f"Expected a JSON object in {path}")
        for ref, value in raw_data.items():
            if not isinstance(ref, str) or not isinstance(value, (int, float)):
                raise RuntimeError(
                    f"Invalid dynamic override entry in {path}: {ref!r}={value!r}"
                )
            overrides[ref] = float(value)

    for override in inline_overrides:
        if "=" not in override:
            raise RuntimeError(
                f"Dynamic override must use REF=VALUE syntax: {override!r}"
            )
        ref, value_text = override.rsplit("=", 1)
        ref = ref.strip()
        if not ref:
            raise RuntimeError(f"Dynamic override is missing a ref: {override!r}")
        try:
            overrides[ref] = float(value_text.strip())
        except ValueError as exc:
            raise RuntimeError(
                f"Dynamic override value must be numeric: {override!r}"
            ) from exc

    return overrides


def load_hero_name_overrides(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    raw_data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw_data, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")

    overrides: dict[str, str] = {}
    for hero_id, display_name in raw_data.items():
        if not isinstance(hero_id, str) or not isinstance(display_name, str):
            raise RuntimeError(
                f"Invalid hero name override entry in {path}: "
                f"{hero_id!r}={display_name!r}"
            )
        overrides[hero_id] = display_name

    return overrides


def extract_function_body(path: Path, signature: str) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.find(signature)
    if start == -1:
        raise RuntimeError(f"Unable to find {signature} in {path}")

    brace_start = text.find("{", start)
    if brace_start == -1:
        raise RuntimeError(f"Unable to find opening brace for {signature} in {path}")

    depth = 0
    for index in range(brace_start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[brace_start + 1 : index]

    raise RuntimeError(f"Unable to find closing brace for {signature} in {path}")


def load_difficulties(
    strings: dict[str, str], resolver: DynamicValueResolver
) -> list[DifficultyRecord]:
    body = extract_function_body(LIB_AFFX_SOURCE_PATH, "string libAffx_GetDifficulty()")
    matches = re.findall(
        r"libAffx_difficulty\s*==\s*(\d+)\s*\)\s*\{\s*return\s+\" \(([^\"\r\n]+)\)\";",
        body,
        flags=re.MULTILINE,
    )
    if not matches:
        raise RuntimeError(
            f"Unable to extract difficulty values from {LIB_AFFX_SOURCE_PATH}"
        )

    name_key_by_value = {
        value: key for key, value in strings.items() if key.startswith("Button/Name/")
    }

    difficulties: list[DifficultyRecord] = []
    for value_text, label in matches:
        localized_name_key = name_key_by_value.get(label, "")
        localized_tooltip_key = (
            localized_name_key.replace("Button/Name/", "Button/Tooltip/")
            if localized_name_key
            else ""
        )
        tooltip = strings.get(localized_tooltip_key, "")
        tooltip_html, tooltip_plain = convert_storm_markup(tooltip, resolver)
        difficulties.append(
            DifficultyRecord(
                difficulty_value=int(value_text),
                label=label,
                localized_name_key=localized_name_key,
                localized_tooltip_key=localized_tooltip_key,
                tooltip_html=tooltip_html,
                tooltip_plain=tooltip_plain,
            )
        )

    return sorted(difficulties, key=lambda item: item.difficulty_value)


def instance_fields(instance: ET.Element) -> dict[str, str]:
    values: dict[str, str] = {}
    for child in instance:
        field = child.find("Field")
        if field is None or "Index" in field.attrib:
            continue
        field_id = field.attrib.get("Id")
        if not field_id:
            continue
        for attr_name in ("String", "Int", "value", "Value"):
            if attr_name in child.attrib:
                values[field_id] = child.attrib[attr_name]
                break
        else:
            values[field_id] = ""
    return values


def is_affix_enabled(fields: dict[str, str]) -> bool:
    enabled_value = fields.get("Enabled", "1").strip()
    return enabled_value not in {"", "0"}


def icon_file_name(icon_path: str) -> str:
    stem = Path(icon_path).stem.strip().lower().replace("-", "_")
    return f"{stem}.png" if stem else ""


def resolve_icon_url(
    icon_path: str,
    icon_dir: Path,
    cache: dict[str, tuple[str, bool]],
) -> tuple[str, bool]:
    if icon_path in cache:
        return cache[icon_path]

    icon_name = icon_file_name(icon_path)
    if icon_name and (icon_dir / icon_name).exists():
        cache[icon_path] = (f"icons/{icon_name}", False)
    else:
        print("Icon not found")
        raise
    return cache[icon_path]


def load_affixes(
    strings: dict[str, str],
    output_dir: Path,
    resolver: DynamicValueResolver,
    hero_name_overrides: Mapping[str, str],
) -> list[AffixRecord]:
    tree = ET.parse(AFFIX_DATA_PATH)
    affix_user = tree.find(".//CUser[@id='Affix']")
    if affix_user is None:
        raise RuntimeError(f"Unable to find Affix definitions in {AFFIX_DATA_PATH}")

    icon_dir = output_dir / "icons"

    default_instance = affix_user.find("./Instances[@Id='[Default]']")
    default_fields = (
        instance_fields(default_instance) if default_instance is not None else {}
    )
    icon_cache: dict[str, tuple[str, bool]] = {}
    affixes: list[AffixRecord] = []

    for instance in affix_user.findall("./Instances"):
        affix_id = instance.attrib.get("Id", "")
        if not affix_id or affix_id == "[Default]":
            continue

        fields = {**default_fields, **instance_fields(instance)}
        if not is_affix_enabled(fields):
            continue

        name_key = f"Affix/Name/{affix_id}"
        tooltip_key = f"Affix/Tooltip/{affix_id}"
        name = strings.get(name_key)
        tooltip = strings.get(tooltip_key)
        if name is None or tooltip is None:
            continue

        tooltip_html, tooltip_plain = convert_storm_markup(tooltip, resolver)
        icon_path = fields.get("Icon", default_fields.get("Icon", ""))
        icon_name = icon_file_name(icon_path)
        icon_url, uses_placeholder = resolve_icon_url(
            icon_path,
            icon_dir,
            icon_cache,
        )
        negative = fields.get("Negative", "0") == "1"
        rarity = fields.get("Rarity", "Common") or "Common"
        hero_specific_raw = fields.get("HeroSpecific", "")
        hero_specific = hero_name_overrides.get(hero_specific_raw, hero_specific_raw)

        affixes.append(
            AffixRecord(
                affix_id=affix_id,
                name=name,
                tooltip_html=tooltip_html,
                tooltip_plain=tooltip_plain,
                rarity=rarity,
                icon_name=icon_name,
                icon_url=icon_url,
                negative=negative,
                hero_specific=hero_specific,
                hero_specific_raw=hero_specific_raw,
                uses_placeholder=uses_placeholder,
            )
        )

    return sorted(
        affixes,
        key=lambda item: (
            item.negative,
            (
                RARITY_ORDER.index(item.rarity)
                if item.rarity in RARITY_ORDER
                else len(RARITY_ORDER)
            ),
            item.name.lower(),
            item.affix_id.lower(),
        ),
    )
