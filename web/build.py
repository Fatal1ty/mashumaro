#!/usr/bin/env python3
"""
Build script for mashumaro documentation site.

Reads markdown files from docs/ directory, converts them to HTML,
and injects them into the landing page template to produce a single index.html.

Usage:  python build.py
Output: dist/index.html and static assets

Markdown files in docs/ are numbered for ordering: 01-getting-started.md, etc.
Each file must have YAML front matter:

    ---
    title: Getting Started
    group: Customization     # optional: groups items under a label in sidebar
    ---

Cross-reference other doc pages with: [Link Text](#/docs/slug-name)

Highlight important content with GitHub-style callouts:

    > [!WARNING]
    > The warning text, with optional inline Markdown.

Supported callout types are NOTE, TIP, IMPORTANT, WARNING, and CAUTION.
"""

import builtins
import html as html_module
import io
import json
import keyword
import os
import re
import shutil
import sys
import token
import tokenize
import tomllib

OG_IMAGE = "og.jpg"
FAVICON = "favicon.svg"
PYTHON_CLASSIFIER_PREFIX = "Programming Language :: Python :: "


def load_project_metadata(web_dir: str) -> dict[str, str]:
    pyproject_path = os.path.join(os.path.dirname(web_dir), "pyproject.toml")
    if not os.path.isfile(pyproject_path):
        print(
            f"Error: pyproject.toml not found at {pyproject_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(pyproject_path, "rb") as f:
        project = tomllib.load(f).get("project", {})

    package_version = project.get("version")
    if not isinstance(package_version, str) or not package_version:
        print("Error: project.version is missing", file=sys.stderr)
        sys.exit(1)

    python_versions = []
    for classifier in project.get("classifiers", []):
        if not isinstance(classifier, str):
            continue
        value = classifier.removeprefix(PYTHON_CLASSIFIER_PREFIX)
        if value != classifier and re.fullmatch(r"\d+\.\d+", value):
            python_versions.append(value)
    python_versions.sort(key=lambda value: tuple(map(int, value.split("."))))
    if not python_versions:
        print(
            "Error: no supported Python versions in project.classifiers",
            file=sys.stderr,
        )
        sys.exit(1)

    min_python = python_versions[0]
    max_python = python_versions[-1]
    python_range = (
        min_python
        if min_python == max_python
        else f"{min_python}–{max_python}"
    )
    return {
        "PACKAGE_VERSION": package_version,
        "MIN_PYTHON_VERSION": min_python,
        "MAX_PYTHON_VERSION": max_python,
        "PYTHON_VERSION_RANGE": python_range,
    }


def substitute_project_metadata(text: str, metadata: dict[str, str]) -> str:
    for name, value in metadata.items():
        text = text.replace(f"{{{{{name}}}}}", value)
    return text


def parse_markdown_to_html(
    md_text: str,
) -> tuple[str, str, str, str, list[dict[str, str | int]]]:
    title = ""
    group = ""
    slug = ""
    if md_text.startswith("---"):
        end = md_text.index("---", 3)
        for line in md_text[3:end].strip().split("\n"):
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip()
            if line.startswith("group:"):
                group = line.split(":", 1)[1].strip()
            if line.startswith("slug:"):
                slug = line.split(":", 1)[1].strip()
        md_text = md_text[end + 3 :].strip()

    lines = md_text.split("\n")
    result = []
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    in_table = False
    table_rows: list[str] = []
    in_bq = False
    bq_lines: list[str] = []
    in_list = False
    list_items: list[str] = []
    headings: list[dict[str, str | int]] = []

    # Track heading slugs within a single doc page to ensure uniqueness
    heading_slug_counts: dict[str, int] = {}

    def make_heading_id(text: str) -> str:
        """Return a URL-friendly, unique id for a heading within the current doc page."""
        base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
        # Fallback if heading contains no ASCII letters/digits
        if not base:
            base = "section"
        cnt = heading_slug_counts.get(base, 0) + 1
        heading_slug_counts[base] = cnt
        return base if cnt == 1 else f"{base}-{cnt}"

    def flush_list() -> None:
        nonlocal in_list, list_items
        if in_list and list_items:
            r = '<ul class="doc-list">\n'
            for li in list_items:
                r += f"<li>{inline(li)}</li>\n"
            result.append(r + "</ul>\n")
            list_items, in_list = [], False

    def flush_bq() -> None:
        nonlocal in_bq, bq_lines
        if in_bq and bq_lines:
            callout_match = re.fullmatch(
                r"\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\\?",
                bq_lines[0],
                flags=re.IGNORECASE,
            )
            if callout_match:
                callout_type = callout_match.group(1).lower()
                callout_labels = {
                    "note": "Note",
                    "tip": "Tip",
                    "important": "Important",
                    "warning": "Warning",
                    "caution": "Caution",
                }
                callout_icons = {
                    "note": (
                        '<circle cx="12" cy="12" r="9"/>'
                        '<path d="M12 11v5"/><path d="M12 8h.01"/>'
                    ),
                    "tip": (
                        '<path d="M9 18h6"/><path d="M10 22h4"/>'
                        '<path d="M8.4 14.5A7 7 0 1 1 15.6 14.5C14.6 15.3 14 16.2 14 18h-4c0-1.8-.6-2.7-1.6-3.5Z"/>'
                    ),
                    "important": (
                        '<circle cx="12" cy="12" r="9"/>'
                        '<path d="M12 7v6"/><path d="M12 17h.01"/>'
                    ),
                    "warning": (
                        '<path d="M10.3 3.7 2.4 18a2 2 0 0 0 1.8 3h15.6a2 2 0 0 0 1.8-3L13.7 3.7a2 2 0 0 0-3.4 0Z"/>'
                        '<path d="M12 9v4"/><path d="M12 17h.01"/>'
                    ),
                    "caution": (
                        '<path d="M7.8 2h8.4L22 7.8v8.4L16.2 22H7.8L2 16.2V7.8Z"/>'
                        '<path d="M12 7v6"/><path d="M12 17h.01"/>'
                    ),
                }
                label = callout_labels[callout_type]
                body = " ".join(bq_lines[1:]).strip()
                body_html = f"<p>{inline(body)}</p>" if body else ""
                result.append(
                    f'<aside class="doc-callout doc-callout-{callout_type}" '
                    f'role="note" aria-label="{label}">'
                    f'<div class="doc-callout-title">'
                    f'<svg class="doc-callout-icon" viewBox="0 0 24 24" '
                    f'fill="none" stroke="currentColor" stroke-width="2" '
                    f'stroke-linecap="round" stroke-linejoin="round" '
                    f'aria-hidden="true">{callout_icons[callout_type]}</svg>'
                    f"<span>{label}</span></div>{body_html}</aside>\n"
                )
            else:
                result.append(
                    f'<blockquote class="doc-quote"><p>'
                    f'{inline(" ".join(bq_lines))}</p></blockquote>\n'
                )
            bq_lines, in_bq = [], False

    def flush_table() -> None:
        nonlocal in_table, table_rows
        if in_table and table_rows:
            r = '<div class="doc-table-wrap"><table class="doc-table">\n'
            for idx, row in enumerate(table_rows):
                cells = split_table_row(row)
                if idx == 0:
                    r += "<thead><tr>" + "".join(
                        f"<th>{inline(c)}</th>" for c in cells
                    )
                    r += "</tr></thead>\n<tbody>\n"
                elif idx == 1:
                    continue
                else:
                    r += (
                        "<tr>"
                        + "".join(f"<td>{inline(c)}</td>" for c in cells)
                        + "</tr>\n"
                    )
            result.append(r + "</tbody></table></div>\n")
            table_rows, in_table = [], False

    def split_table_row(row: str) -> list[str]:
        """Split a Markdown table row without breaking pipes in inline code."""
        cells: list[str] = []
        cell: list[str] = []
        in_code = False
        escaped = False
        for char in row.strip().strip("|"):
            if escaped:
                cell.append(char)
                escaped = False
            elif char == "\\":
                cell.append(char)
                escaped = True
            elif char == "`":
                in_code = not in_code
                cell.append(char)
            elif char == "|" and not in_code:
                cells.append("".join(cell).strip())
                cell = []
            else:
                cell.append(char)
        cells.append("".join(cell).strip())
        return cells

    def highlight_python(code: str) -> str:
        """Highlight Python without changing whitespace or requiring a parser."""
        source_lines = code.splitlines(keepends=True)
        line_offsets: list[int] = []
        offset = 0
        for source_line in source_lines:
            line_offsets.append(offset)
            offset += len(source_line)

        def absolute_offset(position: tuple[int, int]) -> int:
            row, column = position
            if row <= 0 or row > len(line_offsets):
                return len(code)
            return line_offsets[row - 1] + column

        try:
            python_tokens = list(
                tokenize.generate_tokens(io.StringIO(code).readline)
            )
        except (IndentationError, tokenize.TokenError):
            return html_module.escape(code)

        builtin_names = set(dir(builtins))
        type_names = {
            "Any",
            "Annotated",
            "ClassVar",
            "Final",
            "Generic",
            "Literal",
            "LiteralString",
            "Mapping",
            "NamedTuple",
            "Never",
            "NewType",
            "NoReturn",
            "NotRequired",
            "Optional",
            "Protocol",
            "ReadOnly",
            "Required",
            "Self",
            "Sequence",
            "TypeAlias",
            "TypedDict",
            "TypeVar",
            "TypeVarTuple",
            "Union",
            "Unpack",
        }
        known_modules = {
            "collections",
            "dataclasses",
            "datetime",
            "decimal",
            "enum",
            "fractions",
            "ipaddress",
            "json",
            "mashumaro",
            "orjson",
            "pathlib",
            "re",
            "tomllib",
            "typing",
            "typing_extensions",
            "uuid",
            "zoneinfo",
        }
        operator_values = {
            "+",
            "-",
            "*",
            "**",
            "/",
            "//",
            "%",
            "@",
            "<<",
            ">>",
            "&",
            "|",
            "^",
            "~",
            ":=",
            "<",
            "<=",
            ">",
            ">=",
            "==",
            "!=",
            "=",
            "->",
        }

        output: list[str] = []
        last_offset = 0
        declaration = ""
        import_context = False
        decorator_context = False
        previous_significant = ""
        soft_keywords = {"match", "case", "_", "type"}

        for token_info in python_tokens:
            start = absolute_offset(token_info.start)
            end = absolute_offset(token_info.end)
            if start < last_offset:
                continue
            output.append(html_module.escape(code[last_offset:start]))

            value = token_info.string
            token_name = token.tok_name.get(token_info.type, "")
            css_class = ""

            if token_info.type == tokenize.COMMENT:
                css_class = "cm"
            elif token_info.type == tokenize.STRING or token_name.startswith(
                "FSTRING_"
            ):
                css_class = "st"
            elif token_info.type == tokenize.NUMBER:
                css_class = "nr"
            elif token_info.type == tokenize.OP:
                if value == "@":
                    css_class = "dc"
                    decorator_context = True
                elif value in operator_values:
                    css_class = "py-op"
                if value == "(" and decorator_context:
                    decorator_context = False
            elif token_info.type == tokenize.NAME:
                if declaration:
                    css_class = "fn" if declaration == "def" else "cl"
                    declaration = ""
                elif value in {"True", "False", "None", "Ellipsis"}:
                    css_class = "nr"
                elif keyword.iskeyword(value) or value in soft_keywords:
                    css_class = "kw"
                    if value in {"class", "def", "type"}:
                        declaration = value
                    if value in {"from", "import"}:
                        import_context = True
                elif decorator_context:
                    css_class = "dc"
                elif previous_significant == ".":
                    css_class = "py-attr"
                elif import_context or value in known_modules:
                    css_class = "py-mod"
                elif value in {"self", "cls"}:
                    css_class = "py-self"
                elif value in type_names or value[:1].isupper():
                    css_class = "cl"
                elif value in builtin_names:
                    css_class = "nb"

            escaped_value = html_module.escape(value)
            if css_class and value:
                output.append(
                    f'<span class="{css_class}">{escaped_value}</span>'
                )
            else:
                output.append(escaped_value)
            last_offset = end

            if token_info.type == tokenize.NEWLINE:
                import_context = False
                decorator_context = False
                declaration = ""
                previous_significant = ""
            elif value.strip():
                previous_significant = value

        output.append(html_module.escape(code[last_offset:]))
        return "".join(output)

    def highlight_json(code: str) -> str:
        """Highlight JSON keys, strings, numbers, and literals."""
        token_pattern = re.compile(
            r'("(?:\\.|[^"\\])*")(?=\s*:)|'
            r'("(?:\\.|[^"\\])*")|'
            r"(-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)|"
            r"\b(true|false|null)\b"
        )
        output: list[str] = []
        last = 0
        for match in token_pattern.finditer(code):
            output.append(html_module.escape(code[last : match.start()]))
            value = html_module.escape(match.group(0))
            if match.group(1):
                css_class = "py-key"
            elif match.group(2):
                css_class = "st"
            elif match.group(3):
                css_class = "nr"
            else:
                css_class = "kw"
            output.append(f'<span class="{css_class}">{value}</span>')
            last = match.end()
        output.append(html_module.escape(code[last:]))
        return "".join(output)

    def highlight_bash(code: str) -> str:
        """Tokenizer-based syntax highlighting for bash/shell commands."""
        code = html_module.escape(code)
        highlighted_lines = []
        for line in code.split("\n"):
            tokens = []
            i = 0
            n = len(line)
            while i < n:
                if line[i] == "#":
                    tokens.append(("cm", line[i:]))
                    break
                if line[i] == "$":
                    m = re.match(
                        r"\$\{[^}]+\}|\$\([^)]+\)|\$[a-zA-Z_]\w*", line[i:]
                    )
                    if m:
                        tokens.append(("sh-var", m.group()))
                        i += len(m.group())
                        continue
                    tokens.append(("", line[i]))
                    i += 1
                    continue
                if line[i] == "-" and i > 0 and line[i - 1] == " ":
                    m = re.match(r"--?[a-zA-Z][\w-]*", line[i:])
                    if m:
                        tokens.append(("sh-flag", m.group()))
                        i += len(m.group())
                        continue
                if line[i : i + 6] == "&quot;":
                    end = line.find("&quot;", i + 6)
                    if end >= 0:
                        tokens.append(("st", line[i : end + 6]))
                        i = end + 6
                    else:
                        tokens.append(("", line[i : i + 6]))
                        i += 6
                    continue
                if line[i : i + 6] == "&#x27;":
                    end = line.find("&#x27;", i + 6)
                    if end >= 0:
                        tokens.append(("st", line[i : end + 6]))
                        i = end + 6
                    else:
                        tokens.append(("", line[i : i + 6]))
                        i += 6
                    continue
                m = re.match(r"[a-zA-Z_][\w.-]*", line[i:])
                if m:
                    word = m.group()
                    before = line[:i].rstrip()
                    is_cmd = (
                        before == ""
                        or before.endswith("|")
                        or before.endswith(";")
                        or before.endswith("&&")
                        or before.endswith("||")
                    )
                    builtins = {
                        "pip",
                        "pip3",
                        "python",
                        "python3",
                        "curl",
                        "wget",
                        "npm",
                        "npx",
                        "cd",
                        "ls",
                        "mkdir",
                        "cat",
                        "echo",
                        "export",
                        "sudo",
                        "apt",
                        "brew",
                        "git",
                        "docker",
                        "make",
                        "cargo",
                        "go",
                        "yarn",
                    }
                    if is_cmd and (word in builtins or not before):
                        tokens.append(("sh-cmd", word))
                    elif word in {
                        "install",
                        "run",
                        "build",
                        "add",
                        "update",
                        "init",
                        "start",
                        "test",
                        "exec",
                        "push",
                        "pull",
                        "clone",
                        "checkout",
                    }:
                        tokens.append(("sh-sub", word))
                    else:
                        tokens.append(("", word))
                    i += len(word)
                    continue
                if line[i] in "|;&><":
                    tokens.append(("sh-op", line[i]))
                    i += 1
                    continue
                tokens.append(("", line[i]))
                i += 1
            parts = []
            for cls, val in tokens:
                parts.append(
                    f'<span class="{cls}">{val}</span>' if cls else val
                )
            highlighted_lines.append("".join(parts))
        return "\n".join(highlighted_lines)

    def inline(text: str) -> str:
        code_spans: list[str] = []

        def stash_code(m: re.Match[str]) -> str:
            code_spans.append(m.group(1))
            return f"\x00INLINE_CODE_{len(code_spans) - 1}\x00"

        text = re.sub(r"`([^`]+)`", stash_code, text)
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(
            r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text
        )

        def replace_link(m: re.Match[str]) -> str:
            label, href = m.group(1), m.group(2)
            if href.startswith("#/docs/"):
                rest = href[7:]
                if "#" in rest:
                    slug, heading = rest.split("#", 1)
                else:
                    slug, heading = rest, ""
                heading_attr = f' data-heading="{heading}"' if heading else ""
                return (
                    f'<a href="javascript:void(0)" class="doc-xref" '
                    f'data-doc="{slug}"{heading_attr}>{label}</a>'
                )
            elif href.startswith("#"):
                return f'<a href="{href}">{label}</a>'
            return (
                f'<a href="{href}" target="_blank" rel="noopener">{label}</a>'
            )

        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, text)
        for idx, code_span in enumerate(code_spans):
            text = text.replace(
                f"\x00INLINE_CODE_{idx}\x00",
                f"<code>{html_module.escape(code_span)}</code>",
            )
        return text

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                flush_list()
                flush_bq()
                flush_table()
                code_lang = line.strip()[3:].strip()
                code_lines = []
            else:
                in_code = False
                ct = "\n".join(code_lines)
                normalized_lang = code_lang.lower()
                if normalized_lang in ("bash", "sh", "shell", "zsh"):
                    ch = highlight_bash(ct)
                elif normalized_lang in ("python", "py", "", "text"):
                    ch = highlight_python(ct)
                elif normalized_lang == "json":
                    ch = highlight_json(ct)
                else:
                    ch = html_module.escape(ct)
                ll = (
                    "signature"
                    if normalized_lang == "text"
                    else (normalized_lang or "python")
                )
                language_class = re.sub(
                    r"[^a-z0-9_-]+", "-", normalized_lang or "python"
                )
                result.append(
                    f'<div class="doc-code language-{language_class}">'
                    f'<div class="doc-code-header"><span>{ll}</span></div>'
                    f"<pre><code>{ch}</code></pre></div>\n"
                )
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                flush_list()
                flush_bq()
                in_table = True
                table_rows = []
            table_rows.append(line)
            i += 1
            continue
        else:
            flush_table()
        if line.strip().startswith(">"):
            if not in_bq:
                flush_list()
                in_bq = True
                bq_lines = []
            bq_lines.append(line.strip()[1:].strip())
            i += 1
            continue
        else:
            flush_bq()
        if re.match(r"^[-*]\s", line.strip()):
            if not in_list:
                in_list = True
                list_items = []
            list_items.append(line.strip()[2:])
            i += 1
            continue
        else:
            flush_list()
        m = re.match(r"^(#{1,4})\s+(.+)", line)
        if m:
            lv, txt = len(m.group(1)), m.group(2)
            hid = make_heading_id(txt)
            if lv in (2, 3):
                headings.append({"level": lv, "title": txt, "id": hid})
            # Anchor link button (handled by JS in template.html)
            anchor_btn = (
                f'<a class="doc-anchor" href="#{hid}" '
                f'aria-label="Copy link to this section" '
                f'data-heading-id="{hid}">'
                f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                f'stroke-linecap="round" stroke-linejoin="round">'
                f'<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>'
                f'<path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>'
                f"</svg></a>"
            )
            result.append(
                f'<h{lv} class="doc-h{lv}" id="{hid}">'
                f'<span class="doc-h-text">{inline(txt)}</span>'
                f"{anchor_btn}"
                f"</h{lv}>\n"
            )
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        pl = [line]
        i += 1
        while (
            i < len(lines)
            and lines[i].strip()
            and not lines[i].strip().startswith("#")
            and not lines[i].strip().startswith("```")
            and not lines[i].strip().startswith("|")
            and not lines[i].strip().startswith(">")
            and not re.match(r"^[-*]\s", lines[i].strip())
        ):
            pl.append(lines[i])
            i += 1
        result.append(
            f'<p class="doc-p">'
            f'{inline(" ".join(paragraph_line.strip() for paragraph_line in pl))}'
            f"</p>\n"
        )
    flush_list()
    flush_bq()
    flush_table()
    return title, group, slug, "".join(result), headings


def build() -> None:
    web_dir = os.path.dirname(os.path.abspath(__file__))
    project_metadata = load_project_metadata(web_dir)
    docs_dir = os.path.join(web_dir, "docs")
    template_path = os.path.join(web_dir, "template.html")
    dist_dir = os.path.join(web_dir, "dist")

    if not os.path.isdir(docs_dir):
        print(f"Error: docs/ not found at {docs_dir}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(template_path):
        print(
            f"Error: template.html not found at {template_path}",
            file=sys.stderr,
        )
        sys.exit(1)
    og_image_path = os.path.join(web_dir, OG_IMAGE)
    if not os.path.isfile(og_image_path):
        print(
            f"Error: {OG_IMAGE} not found at {og_image_path}", file=sys.stderr
        )
        sys.exit(1)
    favicon_path = os.path.join(web_dir, FAVICON)
    if not os.path.isfile(favicon_path):
        print(f"Error: {FAVICON} not found at {favicon_path}", file=sys.stderr)
        sys.exit(1)

    sections = []
    for fname in sorted(os.listdir(docs_dir)):
        if not fname.endswith(".md"):
            continue
        with open(os.path.join(docs_dir, fname), encoding="utf-8") as f:
            content = substitute_project_metadata(f.read(), project_metadata)
        t, g, explicit_slug, hc, headings = parse_markdown_to_html(content)
        slug = explicit_slug or re.sub(r"[^a-z0-9]+", "-", t.lower()).strip(
            "-"
        )
        sections.append(
            {
                "title": t,
                "slug": slug,
                "html": hc,
                "group": g,
                "headings": headings,
            }
        )

    if not sections:
        print("Error: no .md files in docs/", file=sys.stderr)
        sys.exit(1)

    section_index: dict[str, set[str]] = {}
    for section in sections:
        slug = str(section["slug"])
        if slug in section_index:
            print(
                f"Error: duplicate documentation slug {slug}", file=sys.stderr
            )
            sys.exit(1)
        section_index[slug] = set(
            re.findall(r' id="([^"]+)"', str(section["html"]))
        )

    for section in sections:
        for match in re.finditer(
            r'class="doc-xref" data-doc="([^"]+)"(?: data-heading="([^"]+)")?',
            str(section["html"]),
        ):
            target_slug, target_heading = match.groups()
            if target_slug not in section_index:
                print(
                    f'Error: {section["title"]} links to unknown doc '
                    f"{target_slug}",
                    file=sys.stderr,
                )
                sys.exit(1)
            if (
                target_heading
                and target_heading not in section_index[target_slug]
            ):
                print(
                    f'Error: {section["title"]} links to unknown heading '
                    f"{target_slug}#{target_heading}",
                    file=sys.stderr,
                )
                sys.exit(1)

    # Build nested sidebar
    groups_order = []
    groups_dict: dict[str, list[dict[str, str]]] = {}
    ungrouped = []
    for s in sections:
        if s["group"]:
            if s["group"] not in groups_dict:
                groups_order.append(s["group"])
                groups_dict[s["group"]] = []
            groups_dict[s["group"]].append(s)
        else:
            ungrouped.append(s)

    sidebar = ""
    for s in ungrouped:
        sidebar += f'        <a href="#" class="sidebar-link" data-doc="{s["slug"]}">{s["title"]}</a>\n'
    for gname in groups_order:
        sidebar += '        <div class="sidebar-group">\n'
        sidebar += (
            f'            <div class="sidebar-group-label">{gname}</div>\n'
        )
        for s in groups_dict[gname]:
            sidebar += f'            <a href="#" class="sidebar-link sidebar-link-nested" data-doc="{s["slug"]}">{s["title"]}</a>\n'
        sidebar += "        </div>\n"

    panels = ""
    for s in sections:
        toc_items = ""
        headings = s["headings"]
        for index, heading in enumerate(headings):
            level = int(heading["level"])
            link_classes = f"doc-xref doc-toc-link doc-toc-link-level-{level}"
            if (
                level == 2
                and index + 1 < len(headings)
                and int(headings[index + 1]["level"]) == 3
            ):
                link_classes += " doc-toc-link-has-children"
            toc_items += (
                f'<a class="{link_classes}" '
                f'data-level="{level}" data-doc="{s["slug"]}" '
                f'data-heading="{heading["id"]}" href="javascript:void(0)">'
                f'{html_module.escape(str(heading["title"]))}</a>\n'
            )
        inline_toc = ""
        desktop_toc = ""
        if toc_items:
            inline_toc = (
                '<div class="doc-toc doc-toc-inline" role="navigation" '
                'aria-label="On this page">'
                '<div class="doc-toc-title">On this page</div>'
                f"{toc_items}</div>\n"
            )
            desktop_toc = (
                '<aside class="doc-toc doc-toc-desktop" '
                'aria-label="On this page">'
                '<div class="doc-toc-title">On this page</div>'
                f"{toc_items}</aside>\n"
            )
        panel_html = str(s["html"])
        if inline_toc:
            panel_html = panel_html.replace(
                "</h1>\n", f"</h1>\n{inline_toc}", 1
            )
        panels += (
            f'      <div class="doc-panel" id="doc-{s["slug"]}">\n'
            f'        <article class="doc-main">\n{panel_html}\n'
            f"        </article>\n{desktop_toc}      </div>\n"
        )

    search_entries = []
    for s in sections:
        text = re.sub(r"<[^>]+>", "", s["html"]).replace("\n", " ")
        text = html_module.unescape(re.sub(r"\s+", " ", text).strip())
        search_entries.append(
            {
                "slug": s["slug"],
                "title": s["title"],
                "text": text,
                "heading": "",
            }
        )
        for heading in s["headings"]:
            search_entries.append(
                {
                    "slug": s["slug"],
                    "title": (
                        f'{s["title"]} › '
                        f'{re.sub(r"[`*_]", "", str(heading["title"]))}'
                    ),
                    "text": re.sub(r"[`*_]", "", str(heading["title"])),
                    "heading": heading["id"],
                }
            )

    with open(template_path, encoding="utf-8") as f:
        tmpl = substitute_project_metadata(f.read(), project_metadata)

    for match in re.finditer(
        r'onclick="[^"]*\bshowDocs\(\s*[\'\"]([^\'\"]+)[\'\"]\s*\)', tmpl
    ):
        target_slug = match.group(1)
        if target_slug not in section_index:
            print(
                f"Error: landing page links to unknown doc {target_slug}",
                file=sys.stderr,
            )
            sys.exit(1)

    output = tmpl.replace("{{SIDEBAR_ITEMS}}", sidebar)
    output = output.replace("{{DOC_PANELS}}", panels)
    output = output.replace("{{SEARCH_JSON}}", json.dumps(search_entries))

    unresolved_placeholders = sorted(
        set(re.findall(r"{{[A-Z][A-Z0-9_]*}}", output))
    )
    if unresolved_placeholders:
        print(
            "Error: unresolved placeholders: "
            + ", ".join(unresolved_placeholders),
            file=sys.stderr,
        )
        sys.exit(1)

    if re.search(r"<code>(?:(?!</code>).)*<a\b", output, re.DOTALL):
        print("Error: generated link inside inline code", file=sys.stderr)
        sys.exit(1)
    for href in re.findall(r'<a\b[^>]*\bhref="([^"]*)"', output):
        if not href.startswith(("#", "http://", "https://", "javascript:")):
            print(f"Error: unexpected relative link {href}", file=sys.stderr)
            sys.exit(1)

    os.makedirs(dist_dir, exist_ok=True)
    out_path = os.path.join(dist_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output)

    shutil.copy2(og_image_path, os.path.join(dist_dir, OG_IMAGE))
    shutil.copy2(favicon_path, os.path.join(dist_dir, FAVICON))

    kb = len(output) // 1024
    print(f"  Built {len(sections)} sections into dist/index.html ({kb}KB)")
    print(f"  Copied static asset: {OG_IMAGE}")
    print(f"  Copied static asset: {FAVICON}")


if __name__ == "__main__":
    build()
