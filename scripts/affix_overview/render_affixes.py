from __future__ import annotations

import html
import re

from .constants import RARITY_COLORS, RARITY_DISPLAY_NAMES, RARITY_FILTERS
from .models import AffixRecord
from .render_common import render_page


def render_footer_highlight(value: str) -> str:
    return f'<span class="footer-highlight">{html.escape(value)}</span>'


def render_stackability_html(affix: AffixRecord) -> str:
    if affix.max_stacks == 0:
        return "Stacks infinitely."
    if affix.max_stacks == 1:
        return "Doesn't stack."
    return f"Stacks up to {render_footer_highlight(str(affix.max_stacks))}."


def render_condition_sentence_html(key: str, value: str) -> str:
    highlighted_value = render_footer_highlight(value)
    if key == "hero-specific":
        hero_name = value[:-5] if value.endswith(" only") else value
        return f"Appears for {render_footer_highlight(hero_name)} only."
    if key == "hero-tag":
        return f"Appears for {highlighted_value}."
    if key == "heroes-excluded":
        return f"Does not appear for {highlighted_value}."
    if key == "map-specific":
        map_name = value[:-5] if value.endswith(" only") else value
        return f"Appears on {render_footer_highlight(map_name)} only."
    if key == "maps-excluded":
        return f"Does not appear on {highlighted_value}."
    if key == "affixes-required":
        return f"Requires {highlighted_value}."
    if key == "affixes-excluded":
        return f"Cannot appear with {highlighted_value}."
    if key == "talents-required":
        return f"Requires talents {highlighted_value}."
    if key == "level-range":
        lower_value = value.lower()
        if lower_value.startswith("up to "):
            return f"Appears {render_footer_highlight(lower_value)} only."
        if lower_value.endswith(" only"):
            return f"Appears at {highlighted_value}."
        return f"Appears at {highlighted_value} only."
    return render_footer_highlight(value if value.endswith(".") else f"{value}.")


def render_footer_summary_html(affix: AffixRecord) -> str:
    parts = [render_stackability_html(affix)]
    parts.extend(
        render_condition_sentence_html(condition.key, condition.value)
        for condition in affix.conditions
    )
    return " ".join(parts)


def render_footer_footnote_text_html(text: str) -> str:
    # Only split on sentence-ending periods so hero names like D.Va and E.T.C.
    # remain intact inside highlighted footnotes.
    sentences = [
        match.group(0).strip()
        for match in re.finditer(r".+?(?:\.(?=\s|$)|$)", text)
        if match.group(0).strip()
    ]
    if not sentences:
        return html.escape(text)

    rendered_sentences: list[str] = []
    for sentence in sentences:
        match = re.fullmatch(r"Reduced to (.+?) for (.+)\.", sentence)
        if match is None:
            rendered_sentences.append(html.escape(sentence))
            continue
        reduced_value, heroes = match.groups()
        rendered_sentences.append(
            f"Reduced to {render_footer_highlight(reduced_value)} for {render_footer_highlight(heroes)}."
        )
    return " ".join(rendered_sentences)


def render_footer_footnotes_html(affix: AffixRecord) -> str:
    if not affix.tooltip_footnotes:
        return ""

    items = []
    for footnote in affix.tooltip_footnotes:
        items.append(
            f'<li><span class="footer-footnote-marker">{html.escape(footnote.marker)}</span> {render_footer_footnote_text_html(footnote.text)}</li>'
        )
    return f'<ul class="footer-footnotes">{"".join(items)}</ul>'


AFFIX_PAGE_STYLES = """
    .hero-head {
      display: flex;
      flex-wrap: wrap;
      align-items: end;
      justify-content: space-between;
      gap: 16px;
    }

    .hero h2 {
      margin-bottom: 10px;
    }

    .search {
      width: min(100%, 460px);
      padding: 14px 16px;
      font: inherit;
      color: var(--text);
      background: #0d1522;
      border: 1px solid #31455f;
      border-radius: 14px;
      outline: none;
    }

    .search:focus {
      border-color: var(--accent);
    }

    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .filter-chip {
      border: 1px solid #31455f;
      background: #0f1826;
      color: var(--text);
      border-radius: 999px;
      padding: 10px 14px;
      font: inherit;
      cursor: pointer;
    }

    .filter-chip.active {
      background: #19314c;
      border-color: #4f81b7;
      color: #d9f1ff;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
    }

    .affix-card {
      display: flex;
      flex-direction: column;
      gap: 16px;
      min-height: 100%;
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 22px;
      padding: 18px;
    }

    .affix-card[data-rarity="MythicCurse"] {
      border-color: rgba(255, 91, 110, 0.65);
      box-shadow: inset 0 0 0 1px rgba(255, 91, 110, 0.12);
    }

    .affix-card.hidden {
      display: none;
    }

    .card-top {
      display: grid;
      grid-template-columns: 88px 1fr;
      gap: 14px;
      align-items: start;
    }

    .affix-icon {
      width: 88px;
      height: 88px;
      object-fit: cover;
      border-radius: 18px;
      border: 1px solid #31455f;
      background: #0d1522;
    }

    .card-title {
      margin: 0;
      font-size: 1.18rem;
      line-height: 1.2;
    }

    .meta-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 10px;
    }

    .meta-chip {
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
    }

    .rarity-chip {
      color: var(--rarity-color);
    }

    .affix-card[data-rarity="MythicCurse"] .rarity-chip {
      background: rgba(76, 10, 18, 0.9);
      border-color: rgba(255, 91, 110, 0.4);
    }

    .hero-chip {
      color: #b2d2ff;
    }

    .dynamic-footnote-marker,
    .footer-footnote-marker {
      color: #ffe38d;
      font-weight: 700;
    }

    .footer-highlight {
      color: #ffe38d;
    }

    .card-footer {
      margin-top: auto;
      padding-top: 12px;
      border-top: 1px solid #24344a;
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.5;
      letter-spacing: 0.02em;
    }

    .footer-summary {
      color: var(--muted);
    }

    .footer-footnotes {
      margin: 8px 0 0;
      padding-left: 0;
      list-style: none;
      color: var(--muted);
      font-size: 0.82rem;
      line-height: 1.45;
    }

    .footer-footnotes li + li {
      margin-top: 4px;
    }

    .storm-inline-icon {
      color: #b9dcff;
      margin-right: 0.3em;
    }

    .dynamic-value {
      color: #ffe38d;
      border-bottom: 1px dotted rgba(255, 227, 141, 0.44);
    }

    .empty-state {
      display: none;
      padding: 26px;
      text-align: center;
      color: var(--muted);
      background: var(--panel-alt);
      border: 1px dashed #31455f;
      border-radius: 20px;
    }

    @media (max-width: 720px) {
      .hero-head {
        align-items: stretch;
      }

      .search {
        width: 100%;
      }

      .card-top {
        grid-template-columns: 72px 1fr;
      }

      .affix-icon {
        width: 72px;
        height: 72px;
        border-radius: 14px;
      }
    }
"""


def render_html(affixes: list[AffixRecord], page_type: str, mod_version: str) -> str:
    page_label = "Boons" if page_type == "boon" else "Curses"
    page_label_singular = "boon" if page_type == "boon" else "curse"
    active_page = "boons" if page_type == "boon" else "curses"

    cards = []
    for affix in affixes:
        rarity_color = RARITY_COLORS.get(affix.rarity, "#f2f5f8")
        rarity_label = RARITY_DISPLAY_NAMES.get(affix.rarity, affix.rarity)
        search_blob = " ".join(
            part
            for part in [
                affix.affix_id,
                affix.name,
                affix.tooltip_plain,
                affix.rarity,
                rarity_label,
                affix.hero_specific,
                *(footnote.text for footnote in affix.tooltip_footnotes),
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
        footer_summary_html = render_footer_summary_html(affix)
        footer_footnotes_html = render_footer_footnotes_html(affix)
        cards.append(
            f"""
            <article class="affix-card" data-rarity="{html.escape(affix.rarity)}" data-hero-limited="{str(affix.has_hero_condition).lower()}" data-search="{html.escape(search_blob)}">
              <div class="card-top">
                <img class="affix-icon" src="{html.escape(affix.icon_url)}" alt="{html.escape(affix.name)} icon" loading="lazy">
                <div class="meta-row">
                  <span class="meta-chip rarity-chip" style="--rarity-color: {html.escape(rarity_color)}">{html.escape(rarity_label)}</span>
                  {hero_badge}
                </div>
              </div>
              <h2 class="card-title">{html.escape(affix.name)}</h2>
              <div class="tooltip-copy">{affix.tooltip_html}</div>
              <footer class="card-footer">
                <div class="footer-summary">{footer_summary_html}</div>
                {footer_footnotes_html}
              </footer>
            </article>
            """.strip()
        )

    filter_buttons = "\n        ".join(
        (
            '<button class="filter-chip active" type="button" '
            f'data-rarity-filter="{html.escape(filter_value)}">{html.escape(label)}</button>'
        )
        if filter_value == "all"
        else (
            '<button class="filter-chip" type="button" '
            f'data-rarity-filter="{html.escape(filter_value)}">{html.escape(label)}</button>'
        )
        for filter_value, label in RARITY_FILTERS
    )
    hero_content = f"""      <div class="hero-head">
        <h2>{html.escape(page_label)}</h2>
        <input id="search" class="search" type="search" placeholder="Search by {html.escape(page_label_singular)} name, hero, tooltip, ...">
      </div>
      <div class="filter-row" id="filters">
        {filter_buttons}
      </div>
      <div class="results-note" id="results-note"></div>"""
    body_content = f"""    <section class="grid" id="affix-grid">
      {"".join(cards)}
    </section>

    <div class="empty-state" id="empty-state">No {html.escape(page_label_singular)}s matched the current filter.</div>"""
    script = f"""    const searchInput = document.getElementById("search");
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

    applyFilters();"""
    return render_page(
        active_page=active_page,
        body_content=body_content,
        extra_styles=AFFIX_PAGE_STYLES,
        hero_content=hero_content,
        mod_version=mod_version,
        script=script,
        title=page_label,
    )
