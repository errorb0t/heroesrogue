from __future__ import annotations

import html
from datetime import datetime, timezone

from .models import DifficultyRecord
from .render_common import render_github_link, render_nav


def render_difficulties_html(
    difficulties: list[DifficultyRecord], strings: dict[str, str], mod_version: str
) -> str:
    heading = "Difficulties"

    cards = []
    for difficulty in difficulties:
        tooltip_html = difficulty.tooltip_html or "<p>No localized tooltip found.</p>"
        search_blob = " ".join(
            part
            for part in [
                str(difficulty.difficulty_value),
                difficulty.label,
                difficulty.localized_name_key,
                difficulty.localized_tooltip_key,
                difficulty.tooltip_plain,
            ]
            if part
        ).lower()

        cards.append(
            f"""
            <article class="affix-card" data-search="{html.escape(search_blob)}">
              <h2 class="card-title">{html.escape(difficulty.label)}</h2>
              <div class="tooltip-copy">{tooltip_html}</div>
            </article>
            """.strip()
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Heroes Rogue Wiki - v{html.escape(mod_version)} - Difficulties</title>
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

    .hero h2 {{
      margin: 0;
      font-size: clamp(2rem, 5vw, 3.4rem);
      line-height: 0.95;
      letter-spacing: 0.02em;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 18px;
    }}

    .results-note {{
      color: var(--muted);
      font-size: 0.95rem;
      margin: 0;
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

    .card-title {{
      margin: 0;
      font-size: 1.4rem;
      line-height: 1.15;
    }}

    .tooltip-copy {{
      color: #dce7f9;
      line-height: 1.55;
    }}

    .tooltip-copy br {{
      content: "";
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
      {render_nav("difficulties")}
    </nav>

    <section class="hero">
      <h2>{html.escape(heading)}</h2>
      <div class="results-note">{len(difficulties)} difficulties shown</div>
    </section>

    <section class="grid">
      {"".join(cards)}
    </section>

    <p class="footer-note">This Compendium is generated programmatically and may contain errors. Heroes Rogue is a fan-made project and is not affiliated with or endorsed by Blizzard Entertainment. The mod runs locally and does not interact with Blizzard's servers. All original game assets, characters, and intellectual property belong to Blizzard Entertainment.</p>
  </div>
</body>
</html>
"""
