import re
from pathlib import Path

import pytest

from web.build import html_to_search_text, parse_markdown_to_html


@pytest.mark.parametrize(
    ("callout_type", "label"),
    [
        ("NOTE", "Note"),
        ("TIP", "Tip"),
        ("IMPORTANT", "Important"),
        ("WARNING", "Warning"),
        ("CAUTION", "Caution"),
    ],
)
def test_markdown_callout(callout_type: str, label: str) -> None:
    markdown = (
        f"> [!{callout_type}]\n"
        "> Read the **contract** and use `field_options`."
    )

    html = parse_markdown_to_html(markdown)[3]

    assert f"doc-callout-{callout_type.lower()}" in html
    assert f'aria-label="{label}"' in html
    assert f"<span>{label}</span>" in html
    assert "Read the <strong>contract</strong>" in html
    assert "<code>field_options</code>" in html


def test_markdown_callout_accepts_legacy_line_break_escape() -> None:
    html = parse_markdown_to_html("> [!NOTE]\\\n> Remember this.")[3]

    assert "doc-callout-note" in html
    assert "Remember this." in html


def test_callout_title_is_excluded_from_search_text() -> None:
    html = parse_markdown_to_html(
        "> [!WARNING]\n> Searchable recovery instructions."
    )[3]

    search_text = html_to_search_text(html)

    assert "Warning" not in search_text
    assert "Searchable recovery instructions." in search_text


def test_plain_blockquote_remains_a_quote() -> None:
    html = parse_markdown_to_html("> A quoted passage.")[3]

    assert '<blockquote class="doc-quote">' in html
    assert "doc-callout" not in html


def test_doc_callouts_follow_prose() -> None:
    docs_dir = Path(__file__).parents[1] / "web" / "docs"
    callout_pattern = re.compile(
        r"^> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)]\\?$"
    )
    violations = []

    for path in sorted(docs_dir.glob("*.md")):
        previous_content = ""
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1
        ):
            follows_structural_block = (
                re.match(r"^#{1,4}\s", previous_content)
                or previous_content.startswith(("```", "|", ">"))
                or re.match(r"^(?:[-*]|\d+\.)\s", previous_content)
            )
            if callout_pattern.fullmatch(line) and follows_structural_block:
                violations.append(f"{path.name}:{line_number}")
            if line.strip():
                previous_content = line

    assert not violations, (
        "Callouts must follow prose rather than a structural block: "
        + ", ".join(violations)
    )
