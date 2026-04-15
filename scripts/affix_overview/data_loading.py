from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Mapping

from .constants import (
    AFFIX_DATA_PATH,
    FIELD_VALUE_ATTRIBUTES,
    HERO_TAG_LABELS,
    LIB_AFFX_SOURCE_PATH,
    RARITY_ALIASES,
    RARITY_ORDER,
)
from .dynamic_values import DynamicValueResolver
from .icon_names import icon_file_name
from .markup import convert_storm_markup
from .models import AffixCondition, AffixRecord, DifficultyRecord


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


def load_name_overrides(path: Path, *, label: str) -> dict[str, str]:
    if not path.exists():
        return {}

    raw_data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw_data, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")

    overrides: dict[str, str] = {}
    for raw_key, display_name in raw_data.items():
        if not isinstance(raw_key, str) or not isinstance(display_name, str):
            raise RuntimeError(
                f"Invalid {label} override entry in {path}: "
                f"{raw_key!r}={display_name!r}"
            )
        overrides[raw_key] = display_name

    return overrides


def load_hero_name_overrides(path: Path) -> dict[str, str]:
    return load_name_overrides(path, label="hero name")


def load_map_name_overrides(path: Path) -> dict[str, str]:
    return load_name_overrides(path, label="map name")


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
        tooltip_html, tooltip_plain, _tooltip_footnotes = convert_storm_markup(
            tooltip, resolver
        )
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


def field_child_value(child: ET.Element) -> str:
    if child.tag == "User":
        return child.attrib.get("Instance", "")
    for attr_name in FIELD_VALUE_ATTRIBUTES:
        if attr_name in child.attrib:
            return child.attrib[attr_name]
    return ""


def instance_fields(instance: ET.Element | None) -> dict[str, str]:
    values: dict[str, str] = {}
    if instance is None:
        return values
    for child in instance:
        field = child.find("Field")
        if field is None or "Index" in field.attrib:
            continue
        field_id = field.attrib.get("Id")
        if not field_id:
            continue
        values[field_id] = field_child_value(child)
    return values


def instance_field_lists(instance: ET.Element | None) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    if instance is None:
        return values
    for child in instance:
        field = child.find("Field")
        if field is None:
            continue
        field_id = field.attrib.get("Id")
        if not field_id:
            continue
        values.setdefault(field_id, []).append(field_child_value(child))
    return values


def is_affix_enabled(fields: dict[str, str]) -> bool:
    enabled_value = fields.get("Enabled", "1").strip()
    return enabled_value not in {"", "0"}


def parse_int_field(
    raw_value: str | None, *, default: int = 0, empty_value: int = 0
) -> int:
    if raw_value is None:
        return default
    stripped = raw_value.strip()
    if not stripped:
        return empty_value
    try:
        return int(stripped)
    except ValueError as exc:
        raise RuntimeError(f"Expected integer field value, got {raw_value!r}") from exc


def normalize_affix_rarity(raw_rarity: str | None) -> str:
    if raw_rarity is None:
        return "Common"

    stripped = raw_rarity.strip()
    if not stripped:
        return "Common"

    normalized = RARITY_ALIASES.get(stripped.casefold())
    if normalized is not None:
        return normalized

    condensed = re.sub(r"[\s_-]+", "", stripped.casefold())
    normalized = RARITY_ALIASES.get(condensed)
    if normalized is not None:
        return normalized

    return stripped


def affix_is_curse(fields: Mapping[str, str]) -> bool:
    return parse_int_field(fields.get("Curse"), default=0, empty_value=0) > 0


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
        placeholder_name = "affix_icon_question_mark.png"
        if not (icon_dir / placeholder_name).exists():
            raise RuntimeError(
                f"Icon not found for {icon_path!r} and placeholder {placeholder_name!r} is missing"
            )
        cache[icon_path] = (f"icons/{placeholder_name}", True)
    return cache[icon_path]


def split_semicolon_tags(raw_tags: str) -> list[str]:
    return [tag for tag in (part.strip() for part in raw_tags.split(";")) if tag]


def resolve_affix_name(affix_id: str, strings: Mapping[str, str]) -> str:
    return strings.get(f"Affix/Name/{affix_id}", affix_id)


def resolve_display_name(raw_name: str, overrides: Mapping[str, str]) -> str:
    return overrides.get(raw_name, raw_name)


def append_condition(
    conditions: list[AffixCondition],
    *,
    key: str,
    label: str,
    value: str,
    raw_values: list[str] | None = None,
) -> None:
    search_parts = [label, value]
    if raw_values:
        search_parts.extend(raw_values)
    conditions.append(
        AffixCondition(
            key=key,
            label=label,
            value=value,
            search_text=" ".join(part for part in search_parts if part),
        )
    )


def format_level_condition(min_level: int, max_level: int) -> str:
    if min_level > 0 and max_level > 0:
        if min_level == max_level:
            return f"Level {min_level} only"
        return f"Levels {min_level}-{max_level}"
    if min_level > 0:
        return f"Level {min_level}+"
    if max_level > 0:
        return f"Up to Level {max_level}"
    return ""


def build_affix_conditions(
    fields: Mapping[str, str],
    field_lists: Mapping[str, list[str]],
    strings: Mapping[str, str],
    hero_name_overrides: Mapping[str, str],
    map_name_overrides: Mapping[str, str],
) -> tuple[list[AffixCondition], str, bool]:
    conditions: list[AffixCondition] = []
    hero_specific_raw = fields.get("HeroSpecific", "").strip()
    hero_specific = ""
    has_hero_condition = False

    if hero_specific_raw:
        hero_specific = resolve_display_name(hero_specific_raw, hero_name_overrides)
        append_condition(
            conditions,
            key="hero-specific",
            label="Hero",
            value=f"{hero_specific} only",
            raw_values=[hero_specific_raw, hero_specific],
        )
        has_hero_condition = True
    else:
        hero_tags = split_semicolon_tags(fields.get("HeroTags", ""))
        if hero_tags:
            has_hero_condition = True
            for hero_tag in hero_tags:
                append_condition(
                    conditions,
                    key="hero-tag",
                    label="Heroes",
                    value=HERO_TAG_LABELS.get(hero_tag, hero_tag),
                    raw_values=[hero_tag],
                )

        excluded_heroes = [
            resolve_display_name(hero_id, hero_name_overrides)
            for hero_id in field_lists.get("HeroesExcluded", [])
            if hero_id.strip()
        ]
        if excluded_heroes:
            has_hero_condition = True
            append_condition(
                conditions,
                key="heroes-excluded",
                label="Excludes Heroes",
                value=", ".join(excluded_heroes),
                raw_values=excluded_heroes,
            )

    map_specific_raw = fields.get("MapSpecific", "").strip()
    if map_specific_raw:
        map_name = resolve_display_name(map_specific_raw, map_name_overrides)
        append_condition(
            conditions,
            key="map-specific",
            label="Map",
            value=f"{map_name} only",
            raw_values=[map_specific_raw, map_name],
        )
    else:
        excluded_maps = [
            resolve_display_name(map_id, map_name_overrides)
            for map_id in field_lists.get("MapsExcluded", [])
            if map_id.strip()
        ]
        if excluded_maps:
            append_condition(
                conditions,
                key="maps-excluded",
                label="Excludes Maps",
                value=", ".join(excluded_maps),
                raw_values=excluded_maps,
            )

    required_affixes = [
        resolve_affix_name(required_affix, strings)
        for required_affix in field_lists.get("AffixesRequired", [])
        if required_affix.strip() and required_affix != "[Default]"
    ]
    if required_affixes:
        append_condition(
            conditions,
            key="affixes-required",
            label="Requires Affixes",
            value=", ".join(required_affixes),
            raw_values=required_affixes,
        )

    excluded_affixes = [
        resolve_affix_name(excluded_affix, strings)
        for excluded_affix in field_lists.get("AffixesExcluded", [])
        if excluded_affix.strip() and excluded_affix != "[Default]"
    ]
    if excluded_affixes:
        append_condition(
            conditions,
            key="affixes-excluded",
            label="Excludes Affixes",
            value=", ".join(excluded_affixes),
            raw_values=excluded_affixes,
        )

    required_talents = [
        talent_id for talent_id in field_lists.get("TalentsRequired", []) if talent_id
    ]
    if required_talents:
        append_condition(
            conditions,
            key="talents-required",
            label="Requires Talents",
            value=", ".join(required_talents),
            raw_values=required_talents,
        )

    level_condition = format_level_condition(
        parse_int_field(fields.get("LevelMin"), default=0, empty_value=0),
        parse_int_field(fields.get("LevelMax"), default=0, empty_value=0),
    )
    if level_condition:
        append_condition(
            conditions,
            key="level-range",
            label="Levels",
            value=level_condition,
        )

    return conditions, hero_specific, has_hero_condition


def load_affixes(
    strings: dict[str, str],
    output_dir: Path,
    resolver: DynamicValueResolver,
    hero_name_overrides: Mapping[str, str],
    map_name_overrides: Mapping[str, str],
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
        field_lists = instance_field_lists(instance)
        if not is_affix_enabled(fields):
            continue

        name_key = f"Affix/Name/{affix_id}"
        tooltip_key = f"Affix/Tooltip/{affix_id}"
        name = strings.get(name_key)
        tooltip = strings.get(tooltip_key)
        if name is None or tooltip is None:
            continue

        tooltip_html, tooltip_plain, tooltip_footnotes = convert_storm_markup(
            tooltip, resolver
        )
        icon_path = fields.get("Icon", default_fields.get("Icon", ""))
        icon_name = icon_file_name(icon_path)
        icon_url, uses_placeholder = resolve_icon_url(
            icon_path,
            icon_dir,
            icon_cache,
        )
        max_stacks = parse_int_field(fields.get("Max"), default=1, empty_value=0)
        negative = affix_is_curse(fields)
        rarity = normalize_affix_rarity(fields.get("Rarity"))
        conditions, hero_specific, has_hero_condition = build_affix_conditions(
            fields,
            field_lists,
            strings,
            hero_name_overrides,
            map_name_overrides,
        )

        affixes.append(
            AffixRecord(
                affix_id=affix_id,
                name=name,
                tooltip_html=tooltip_html,
                tooltip_plain=tooltip_plain,
                tooltip_footnotes=tooltip_footnotes,
                rarity=rarity,
                max_stacks=max_stacks,
                icon_name=icon_name,
                icon_url=icon_url,
                negative=negative,
                hero_specific=hero_specific,
                has_hero_condition=has_hero_condition,
                conditions=conditions,
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
