from __future__ import annotations

import html

from .models import AchievementRecord
from .render_common import render_page


ACHIEVEMENT_PAGE_STYLES = """
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

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
    }

    .achievement-card {
      display: grid;
      grid-template-columns: 88px 1fr;
      gap: 14px;
      align-items: start;
      min-height: 100%;
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 22px;
      padding: 18px;
    }

    .achievement-card.hidden {
      display: none;
    }

    .achievement-icon {
      width: 88px;
      height: 88px;
      object-fit: cover;
      border-radius: 18px;
      border: 1px solid #31455f;
      background: #0d1522;
    }

    .card-title {
      margin: 0 0 10px;
      font-size: 1.18rem;
      line-height: 1.2;
    }

    @media (max-width: 720px) {
      .achievement-card {
        border-radius: 18px;
      }
    }
"""


ACHIEVEMENT_PAGE_SCRIPT = """
    const searchInput = document.querySelector("#achievement-search");
    const cards = Array.from(document.querySelectorAll(".achievement-card"));
    const resultsNote = document.querySelector("#results-note");

    function updateAchievements() {
      const query = searchInput.value.trim().toLowerCase();
      let visible = 0;

      for (const card of cards) {
        const matches = !query || card.dataset.search.includes(query);
        card.classList.toggle("hidden", !matches);
        if (matches) visible += 1;
      }

      resultsNote.textContent = `${visible} achievement${visible === 1 ? "" : "s"} shown`;
    }

    searchInput.addEventListener("input", updateAchievements);
"""


def render_achievements_html(
    achievements: list[AchievementRecord], mod_version: str
) -> str:
    cards = []
    for achievement in achievements:
        tooltip_html = achievement.tooltip_html or "No localized tooltip found."
        search_blob = " ".join(
            [
                achievement.achievement_id,
                achievement.name,
                achievement.tooltip_plain,
            ]
        ).lower()
        cards.append(
            f"""
            <article class="achievement-card" data-search="{html.escape(search_blob)}">
              <img class="achievement-icon" src="{html.escape(achievement.icon_url)}" alt="" loading="lazy">
              <div>
                <h2 class="card-title">{html.escape(achievement.name)}</h2>
                <div class="tooltip-copy">{tooltip_html}</div>
              </div>
            </article>
            """.strip()
        )

    hero_content = f"""      <div class="hero-head">
        <div>
          <h2>Achievements</h2>
          <p class="results-note" id="results-note">{len(achievements)} achievements shown</p>
        </div>
        <input class="search" id="achievement-search" type="search" placeholder="Search achievements" aria-label="Search achievements">
      </div>"""
    body_content = f"""    <section class="grid">
      {"".join(cards)}
    </section>"""
    return render_page(
        active_page="achievements",
        body_content=body_content,
        extra_styles=ACHIEVEMENT_PAGE_STYLES,
        hero_content=hero_content,
        mod_version=mod_version,
        script=ACHIEVEMENT_PAGE_SCRIPT,
        title="Achievements",
    )
