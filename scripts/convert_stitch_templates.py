"""One-off: strip duplicate Stitch headers and wrap pages in core/base.html."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates" / "core"

PAGES = [
    "index.html",
    "black_list.html",
    "company.html",
    "background_verification.html",
    "warining_new.html",
    "about_us.html",
    "contact.html",
    "blacklist_profile.html",
    "verification_result.html",
]

NAV_PATH_TO_URL = {
    "home": "{% url 'home' %}",
    "black-list": "{% url 'blacklist' %}",
    "companies": "{% url 'companies' %}",
    "background-verification": "{% url 'verification' %}",
    "warning-news": "{% url 'news' %}",
    "about-us": "{% url 'about' %}",
    "contact": "{% url 'contact' %}",
    "login": "{% url 'login' %}",
    "person-profile": "{% url 'blacklist' %}",
    "company-profile": "{% url 'companies' %}",
}


def fix_navigation_hrefs(html: str) -> str:
    """Replace data-path + href=\"#\" nav links with Django url tags."""

    def repl(match: re.Match[str]) -> str:
        path = match.group(1)
        url = NAV_PATH_TO_URL.get(path)
        if not url:
            return match.group(0)
        return f'href="{url}"'

    html = re.sub(
        r'data-path="([^"]+)"\s+href="#"',
        repl,
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r'href="#"\s+data-path="([^"]+)"',
        lambda m: f'href="{NAV_PATH_TO_URL.get(m.group(1), "#")}"'
        if m.group(1) in NAV_PATH_TO_URL
        else m.group(0),
        html,
        flags=re.IGNORECASE,
    )
    # Appeal / Report in footers
    html = re.sub(
        r'(<a[^>]*>\s*Appeal\s*/\s*Report\s*</a>)',
        lambda m: m.group(0).replace('href="#"', 'href="{% url \'appeal\' %}"')
        if 'href="#"' in m.group(0)
        else m.group(0),
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return html


def extract_body_content(text: str) -> str | None:
    lower = text.lower()
    end_header = lower.find("</header>")
    if end_header == -1:
        return None
    body = text[end_header + len("</header>") :]
    body = re.sub(
        r'<script\s+src="/static/js/guardian\.js"></script>\s*',
        "",
        body,
        flags=re.IGNORECASE,
    )
    body = re.sub(r"</body>\s*</html>\s*$", "", body, flags=re.IGNORECASE | re.DOTALL)
    return body.strip()


def convert_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("{% extends"):
        return False
    body = extract_body_content(text)
    if body is None:
        print(f"skip (no header): {path.name}")
        return False
    body = fix_navigation_hrefs(body)
    title_match = re.search(r"<title>([^<]*)</title>", text, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else "GUARDIAN (PBVS)"
    if title == "GUARDIAN (PBVS)":
        title_block = "{% block title %}GUARDIAN (PBVS){% endblock %}"
    else:
        title_block = f"{{% block title %}}{title}{{% endblock %}}"

    out = (
        f"{{% extends 'core/base.html' %}}\n"
        f"{title_block}\n"
        f"{{% block content %}}\n"
        f"{body}\n"
        f"{{% endblock %}}\n"
    )
    path.write_text(out, encoding="utf-8")
    print(f"converted: {path.name}")
    return True


def main() -> None:
    for name in PAGES:
        p = TEMPLATES / name
        if p.exists():
            convert_file(p)


if __name__ == "__main__":
    main()
