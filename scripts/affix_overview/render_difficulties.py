from __future__ import annotations

import html

from .models import DifficultyRecord
from .render_common import render_page


def render_difficulties_html(
    difficulties: list[DifficultyRecord], mod_version: str
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

    hero_content = f"""      <h2>{html.escape(heading)}</h2>
      <div class="results-note">{len(difficulties)} difficulties shown</div>"""
    body_content = f"""    <section class="grid">
      {"".join(cards)}
    </section>"""
    return render_page(
        active_page="difficulties",
        body_content=body_content,
        extra_styles="""
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
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

    .card-title {
      margin: 0;
      font-size: 1.4rem;
      line-height: 1.15;
    }
""",
        hero_content=hero_content,
        mod_version=mod_version,
        title=heading,
    )
