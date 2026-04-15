from __future__ import annotations

import html

from .constants import FOOTER_NOTE, GITHUB_URL, NAV_ITEMS


def render_nav(active_page: str) -> str:
    links = []
    for href, label, page_key in NAV_ITEMS:
        active_class = " active" if active_page == page_key else ""
        links.append(
            f'<a class="menu-link{active_class}" href="{href}">{html.escape(label)}</a>'
        )
    return "\n      ".join(links)


def render_github_link() -> str:
    return (
        f'<a class="github-link" href="{html.escape(GITHUB_URL)}" '
        'target="_blank" rel="noreferrer">Play Heroes Rogue</a>'
    )


COMMON_PAGE_STYLES = """
    :root {
      --bg: #0c1220;
      --panel: #162133;
      --panel-alt: #111927;
      --panel-border: #24344a;
      --text: #eef4ff;
      --muted: #9eb1cd;
      --accent: #8fd3ff;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      color: var(--text);
      background: var(--bg);
      min-height: 100vh;
    }

    a {
      color: inherit;
      text-decoration: none;
    }

    .shell {
      width: min(1400px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 56px;
    }

    .top-bar {
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }

    .site-header {
      margin: 0;
      font-size: clamp(1.6rem, 3vw, 2.2rem);
      line-height: 1;
      letter-spacing: 0.02em;
    }

    .github-link {
      border: 1px solid #31455f;
      background: #0f1826;
      color: var(--text);
      border-radius: 999px;
      padding: 12px 18px;
      font: inherit;
      white-space: nowrap;
    }

    .top-nav {
      display: flex;
      gap: 10px;
      margin-bottom: 18px;
      flex-wrap: wrap;
    }

    .menu-link {
      border: 1px solid #31455f;
      background: #0f1826;
      color: var(--text);
      border-radius: 999px;
      padding: 12px 18px;
      font: inherit;
    }

    .menu-link.active {
      background: #214161;
      border-color: #74afe6;
      color: #f3fbff;
    }

    .hero {
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 26px;
      padding: 28px;
      display: grid;
      gap: 18px;
      margin-bottom: 28px;
    }

    .hero h2 {
      margin: 0;
      font-size: clamp(2rem, 5vw, 3.4rem);
      line-height: 0.95;
      letter-spacing: 0.02em;
    }

    .results-note {
      margin: 0;
      color: var(--muted);
      font-size: 0.95rem;
    }

    .tooltip-copy {
      color: #dce7f9;
      line-height: 1.55;
    }

    .tooltip-copy br {
      content: "";
    }

    .footer-note {
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.9rem;
    }

    @media (max-width: 720px) {
      .shell {
        width: min(100% - 20px, 1400px);
        padding-top: 20px;
      }

      .hero,
      .affix-card {
        border-radius: 18px;
      }

      .top-bar {
        align-items: stretch;
        flex-direction: column;
      }

      .github-link {
        align-self: flex-start;
      }
    }
"""


def render_page(
    *,
    active_page: str,
    body_content: str,
    extra_styles: str,
    hero_content: str,
    mod_version: str,
    script: str = "",
    title: str,
) -> str:
    script_block = ""
    if script:
        script_block = f"""
  <script>
{script}
  </script>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Heroes Rogue Wiki - v{html.escape(mod_version)} - {html.escape(title)}</title>
  <style>
{COMMON_PAGE_STYLES}
{extra_styles}
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
{hero_content}
    </section>

{body_content}

    <p class="footer-note">{html.escape(FOOTER_NOTE)}</p>
  </div>
{script_block}
</body>
</html>
"""
