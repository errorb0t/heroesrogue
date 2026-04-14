from __future__ import annotations

import html

GITHUB_URL = "https://github.com/sobbyellow/heroesrogue"


def render_nav(active_page: str) -> str:
    nav_items = [
        ("index.html", "Boons", "boons"),
        ("curses.html", "Curses", "curses"),
        ("difficulties.html", "Difficulties", "difficulties"),
    ]
    links = []
    for href, label, page_key in nav_items:
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
