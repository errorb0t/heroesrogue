from __future__ import annotations

import html
from datetime import datetime, timezone

from .constants import RARITY_COLORS
from .models import AffixRecord
from .render_common import render_github_link, render_nav


def render_stackability_label(affix: AffixRecord) -> str:
    if affix.max_stacks == 0:
        return "Stacks infinitely"
    if affix.max_stacks == 1:
        return "Doesn't stack"
    return f"Stacks up to {affix.max_stacks}"


def render_condition_sentence(key: str, value: str) -> str:
    if key == "hero-specific":
        return f"Appears for {value}."
    if key == "hero-tag":
        return f"Appears for {value}."
    if key == "heroes-excluded":
        return f"Does not appear for {value}."
    if key == "map-specific":
        return f"Appears on {value}."
    if key == "maps-excluded":
        return f"Does not appear on {value}."
    if key == "affixes-required":
        return f"Requires {value}."
    if key == "affixes-excluded":
        return f"Cannot appear with {value}."
    if key == "talents-required":
        return f"Requires talents {value}."
    if key == "level-range":
        lower_value = value.lower()
        if lower_value.startswith("up to "):
            return f"Appears {lower_value} only."
        if lower_value.endswith(" only"):
            return f"Appears at {value}."
        return f"Appears at {value} only."
    return value if value.endswith(".") else f"{value}."


def render_footer_text(affix: AffixRecord) -> str:
    parts = [f"{render_stackability_label(affix)}."]
    parts.extend(
        render_condition_sentence(condition.key, condition.value)
        for condition in affix.conditions
    )
    return " ".join(parts)


def render_html(affixes: list[AffixRecord], page_type: str, mod_version: str) -> str:
    page_label = "Boons" if page_type == "boon" else "Curses"
    page_label_singular = "boon" if page_type == "boon" else "curse"
    active_page = "boons" if page_type == "boon" else "curses"

    cards = []
    for affix in affixes:
        rarity_color = RARITY_COLORS.get(affix.rarity, "#f2f5f8")
        search_blob = " ".join(
            part
            for part in [
                affix.affix_id,
                affix.name,
                affix.tooltip_plain,
                affix.rarity,
                affix.hero_specific,
                *(condition.search_text for condition in affix.conditions),
                "curse" if affix.negative else "boon",
            ]
            if part
        ).lower()
        hero_badge = (
            f'<span class="meta-chip hero-chip">{html.escape(affix.hero_specific)}</span>'
            if affix.hero_specific
            else ""
        )
        footer_text = render_footer_text(affix)
        cards.append(
            f"""
            <article class="affix-card" data-rarity="{html.escape(affix.rarity)}" data-hero-limited="{str(affix.has_hero_condition).lower()}" data-search="{html.escape(search_blob)}">
              <div class="card-top">
                <img class="affix-icon" src="{html.escape(affix.icon_url)}" alt="{html.escape(affix.name)} icon" loading="lazy">
                <div class="meta-row">
                  <span class="meta-chip rarity-chip" style="--rarity-color: {html.escape(rarity_color)}">{html.escape(affix.rarity)}</span>
                  {hero_badge}
                </div>
              </div>
              <h2 class="card-title">{html.escape(affix.name)}</h2>
              <div class="tooltip-copy">{affix.tooltip_html}</div>
              <footer class="card-footer">{html.escape(footer_text)}</footer>
            </article>
            """.strip()
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Heroes Rogue Wiki - v{html.escape(mod_version)} - {page_label}</title>
  <style>
    :root {{
      --bg: #0c1220;
      --panel: #162133;
      --panel-alt: #111927;
      --panel-border: #24344a;
      --text: #eef4ff;
      --muted: #9eb1cd;
      --accent: #8fd3ff;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      color: var(--text);
      background: var(--bg);
      min-height: 100vh;
    }}

    a {{
      color: inherit;
      text-decoration: none;
    }}

    .shell {{
      width: min(1400px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 56px;
    }}

    .top-bar {{
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }}

    .site-header {{
      margin: 0;
      font-size: clamp(1.6rem, 3vw, 2.2rem);
      line-height: 1;
      letter-spacing: 0.02em;
    }}

    .github-link {{
      border: 1px solid #31455f;
      background: #0f1826;
      color: var(--text);
      border-radius: 999px;
      padding: 12px 18px;
      font: inherit;
      white-space: nowrap;
    }}

    .top-nav {{
      display: flex;
      gap: 10px;
      margin-bottom: 18px;
      flex-wrap: wrap;
    }}

    .menu-link {{
      border: 1px solid #31455f;
      background: #0f1826;
      color: var(--text);
      border-radius: 999px;
      padding: 12px 18px;
      font: inherit;
    }}

    .menu-link.active {{
      background: #214161;
      border-color: #74afe6;
      color: #f3fbff;
    }}

    .hero {{
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 26px;
      padding: 28px;
      display: grid;
      gap: 18px;
      margin-bottom: 28px;
    }}

    .hero-head {{
      display: flex;
      flex-wrap: wrap;
      align-items: end;
      justify-content: space-between;
      gap: 16px;
    }}

    .hero h2 {{
      margin: 0 0 10px;
      font-size: clamp(2rem, 5vw, 3.4rem);
      line-height: 0.95;
      letter-spacing: 0.02em;
    }}

    .search {{
      width: min(100%, 460px);
      padding: 14px 16px;
      font: inherit;
      color: var(--text);
      background: #0d1522;
      border: 1px solid #31455f;
      border-radius: 14px;
      outline: none;
    }}

    .search:focus {{
      border-color: var(--accent);
    }}

    .filter-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}

    .filter-chip {{
      border: 1px solid #31455f;
      background: #0f1826;
      color: var(--text);
      border-radius: 999px;
      padding: 10px 14px;
      font: inherit;
      cursor: pointer;
    }}

    .filter-chip.active {{
      background: #19314c;
      border-color: #4f81b7;
      color: #d9f1ff;
    }}

    .results-note {{
      color: var(--muted);
      font-size: 0.95rem;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
    }}

    .affix-card {{
      display: flex;
      flex-direction: column;
      gap: 16px;
      min-height: 100%;
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 22px;
      padding: 18px;
    }}

    .affix-card.hidden {{
      display: none;
    }}

    .card-top {{
      display: grid;
      grid-template-columns: 88px 1fr;
      gap: 14px;
      align-items: start;
    }}

    .affix-icon {{
      width: 88px;
      height: 88px;
      object-fit: cover;
      border-radius: 18px;
      border: 1px solid #31455f;
      background: #0d1522;
    }}

    .card-title {{
      margin: 0;
      font-size: 1.18rem;
      line-height: 1.2;
    }}

    .meta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 10px;
    }}

    .meta-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 28px;
      padding: 5px 10px;
      border-radius: 999px;
      font-size: 0.77rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      border: 1px solid #31455f;
      background: #0f1826;
    }}

    .rarity-chip {{
      color: var(--rarity-color);
    }}

    .hero-chip {{
      color: #b2d2ff;
    }}

    .tooltip-copy {{
      color: #dce7f9;
      line-height: 1.55;
    }}

    .card-footer {{
      margin-top: auto;
      padding-top: 12px;
      border-top: 1px solid #24344a;
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.5;
      letter-spacing: 0.02em;
    }}

    .tooltip-copy br {{
      content: "";
    }}

    .storm-inline-icon {{
      color: #b9dcff;
      margin-right: 0.3em;
    }}

    .dynamic-value {{
      color: #ffe38d;
      border-bottom: 1px dotted rgba(255, 227, 141, 0.44);
    }}

    .empty-state {{
      display: none;
      padding: 26px;
      text-align: center;
      color: var(--muted);
      background: var(--panel-alt);
      border: 1px dashed #31455f;
      border-radius: 20px;
    }}

    .footer-note {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.9rem;
    }}

    @media (max-width: 720px) {{
      .shell {{
        width: min(100% - 20px, 1400px);
        padding-top: 20px;
      }}

      .hero,
      .affix-card {{
        border-radius: 18px;
      }}

      .top-bar {{
        align-items: stretch;
        flex-direction: column;
      }}

      .github-link {{
        align-self: flex-start;
      }}

      .hero-head {{
        align-items: stretch;
      }}

      .search {{
        width: 100%;
      }}

      .card-top {{
        grid-template-columns: 72px 1fr;
      }}

      .affix-icon {{
        width: 72px;
        height: 72px;
        border-radius: 14px;
      }}
    }}
  </style>
</head>
  <body>
  <div class="shell">
    <div class="top-bar">
      <h1 class="site-header">Heroes Rogue Compendium (v{html.escape(mod_version)})</h1>
      {render_github_link()}
    </div>
    <nav class="top-nav" aria-label="Sections">
      {render_nav(active_page)}
    </nav>

    <section class="hero">
      <div class="hero-head">
        <h2>{page_label}</h2>
        <input id="search" class="search" type="search" placeholder="Search by {page_label_singular} name, hero, tooltip, ...">
      </div>
      <div class="filter-row" id="filters">
        <button class="filter-chip active" type="button" data-rarity-filter="all">All</button>
        <button class="filter-chip" type="button" data-rarity-filter="hero-limited">Hero-specific</button>
        <button class="filter-chip" type="button" data-rarity-filter="Starter">Starter</button>
        <button class="filter-chip" type="button" data-rarity-filter="Common">Common</button>
        <button class="filter-chip" type="button" data-rarity-filter="Uncommon">Uncommon</button>
        <button class="filter-chip" type="button" data-rarity-filter="Rare">Rare</button>
        <button class="filter-chip" type="button" data-rarity-filter="Epic">Epic</button>
        <button class="filter-chip" type="button" data-rarity-filter="Legendary">Legendary</button>
      </div>
      <div class="results-note" id="results-note"></div>
    </section>

    <section class="grid" id="affix-grid">
      {"".join(cards)}
    </section>

    <div class="empty-state" id="empty-state">No {page_label_singular}s matched the current filter.</div>
    <p class="footer-note">This Compendium is generated programmatically and may contain errors. Heroes Rogue is a fan-made project and is not affiliated with or endorsed by Blizzard Entertainment. The mod runs locally and does not interact with Blizzard's servers. All original game assets, characters, and intellectual property belong to Blizzard Entertainment.</p>
  </div>

  <script>
    const searchInput = document.getElementById("search");
    const rarityButtons = Array.from(document.querySelectorAll(".filter-chip"));
    const cards = Array.from(document.querySelectorAll(".affix-card"));
    const resultsNote = document.getElementById("results-note");
    const emptyState = document.getElementById("empty-state");
    let activeRarity = "all";

    function matchesRarity(card) {{
      if (activeRarity === "all") return true;
      if (activeRarity === "hero-limited") {{
        return card.dataset.heroLimited === "true";
      }}
      return card.dataset.rarity === activeRarity;
    }}

    function applyFilters() {{
      const query = searchInput.value.trim().toLowerCase();
      let visible = 0;

      for (const card of cards) {{
        const searchMatch = !query || card.dataset.search.includes(query);
        const rarityMatch = matchesRarity(card);
        const show = searchMatch && rarityMatch;
        card.classList.toggle("hidden", !show);
        if (show) visible += 1;
      }}

      resultsNote.textContent = `${{visible}} of ${{cards.length}} {page_label_singular}s shown`;
      emptyState.style.display = visible === 0 ? "block" : "none";
    }}

    searchInput.addEventListener("input", applyFilters);
    for (const button of rarityButtons) {{
      button.addEventListener("click", () => {{
        activeRarity = button.dataset.rarityFilter;
        for (const item of rarityButtons) {{
          item.classList.toggle("active", item === button);
        }}
        applyFilters();
      }});
    }}

    applyFilters();
  </script>
</body>
</html>
"""
