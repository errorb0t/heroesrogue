from __future__ import annotations

import argparse
from pathlib import Path

from .constants import (
    DYNAMIC_OVERRIDES_PATH,
    HERO_NAME_OVERRIDES_PATH,
    LIB_AFFX_HEADER_PATH,
    MAP_NAME_OVERRIDES_PATH,
    ROOT,
    STRINGS_PATH,
    TEXTURES_DIR,
)
from .data_loading import (
    load_affixes,
    load_difficulties,
    load_dynamic_value_overrides,
    load_hero_name_overrides,
    load_map_name_overrides,
    load_mod_version,
    load_strings,
)
from .dynamic_values import DynamicValueResolver
from .icon_export import export_texture_icons
from .render_affixes import render_html
from .render_difficulties import render_difficulties_html


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an HTML overview of Heroes Rogue affixes."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs",
        help="Directory where the generated overview should be written.",
    )
    parser.add_argument(
        "--dynamic-overrides",
        type=Path,
        default=DYNAMIC_OVERRIDES_PATH,
        help=(
            "JSON file containing manual dynamic-value overrides as " '{"ref": number}.'
        ),
    )
    parser.add_argument(
        "--dynamic-override",
        action="append",
        default=[],
        metavar="REF=VALUE",
        help="Add or replace a manual dynamic-value override for this run.",
    )
    parser.add_argument(
        "--hero-name-overrides",
        type=Path,
        default=HERO_NAME_OVERRIDES_PATH,
        help='JSON file containing custom hero display names as {"HeroId": "Display Name"}.',
    )
    parser.add_argument(
        "--map-name-overrides",
        type=Path,
        default=MAP_NAME_OVERRIDES_PATH,
        help='JSON file containing custom map display names as {"MapId": "Display Name"}.',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    exported_icons = export_texture_icons(TEXTURES_DIR, output_dir / "icons")

    mod_version = load_mod_version(LIB_AFFX_HEADER_PATH)
    strings = load_strings(STRINGS_PATH)
    dynamic_overrides = load_dynamic_value_overrides(
        args.dynamic_overrides.resolve(), args.dynamic_override
    )
    hero_name_overrides = load_hero_name_overrides(args.hero_name_overrides.resolve())
    map_name_overrides = load_map_name_overrides(args.map_name_overrides.resolve())
    resolver = DynamicValueResolver(dynamic_overrides)
    resolver.set_hero_name_overrides(hero_name_overrides)
    affixes = load_affixes(
        strings,
        output_dir,
        resolver,
        hero_name_overrides,
        map_name_overrides,
    )
    difficulties = load_difficulties(strings, resolver)
    boons = [affix for affix in affixes if not affix.negative]
    curses = [affix for affix in affixes if affix.negative]

    pages = {
        output_dir / "index.html": render_html(boons, "boon", mod_version),
        output_dir / "curses.html": render_html(curses, "curse", mod_version),
        output_dir
        / "difficulties.html": render_difficulties_html(
            difficulties, strings, mod_version
        ),
    }

    for path, html_output in pages.items():
        path.write_text(html_output, encoding="utf-8")
        print(f"Wrote {path}")

    print(f"Enabled affixes: {len(affixes)}")
    print(f"Boons: {len(boons)}")
    print(f"Curses: {len(curses)}")
    print(f"Difficulties: {len(difficulties)}")
    print(f"Exported icons: {exported_icons}")
    missing_icon_names = sorted(
        {
            affix.icon_name
            for affix in affixes
            if affix.uses_placeholder and affix.icon_name
        }
    )
    print(f"Placeholder icons: {len(missing_icon_names)}")
    for icon_name in missing_icon_names:
        print(f"Missing icon file: {icon_name}")
