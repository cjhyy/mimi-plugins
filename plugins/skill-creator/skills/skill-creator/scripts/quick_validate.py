#!/usr/bin/env python3
"""Deterministic SKILL.md validator — Step 4 of skill-creator.

Replaces eyeballing a checklist with hard checks. Pass the path to a SKILL.md
(or the skill directory containing one):

    python3 quick_validate.py path/to/SKILL.md
    python3 quick_validate.py path/to/<skill-dir>

Exit code 0 = all checks pass (warnings allowed), 1 = at least one ERROR.
No third-party deps: a tiny frontmatter scanner, not a full YAML parser, so it
runs anywhere Python 3 does. Output is plain text, one line per finding.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# A description shorter than this rarely carries enough trigger words to fire;
# longer than this risks truncation in the skill list. Soft (warning) bounds.
DESC_MIN = 40
DESC_MAX = 500
# Body past this many lines should be split into reference files (SKILL.md
# guidance: keep it short, link out for detail). Soft.
BODY_MAX_LINES = 150

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def resolve_skill_md(arg: str) -> Path:
    # Resolve to absolute so `.parent.name` is the real dir even when the arg
    # is a bare "SKILL.md" (whose .parent would otherwise be "").
    p = Path(arg).resolve()
    if p.is_dir():
        p = p / "SKILL.md"
    return p


def split_frontmatter(text: str) -> tuple[dict[str, str], list[str]] | None:
    """Return ({key: value}, body_lines) or None if no frontmatter block.

    Only handles the flat `key: value` shape SKILL.md uses; nested YAML is out
    of scope (skills don't need it). Values are taken verbatim (quotes stripped).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm: dict[str, str] = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return fm, lines[i + 1 :]
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
        if m:
            key, val = m.group(1), m.group(2).strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            fm[key] = val
    return None  # opening --- but no closing ---


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: quick_validate.py <SKILL.md | skill-dir>")
        return 2

    skill_md = resolve_skill_md(argv[1])
    errors: list[str] = []
    warnings: list[str] = []

    if not skill_md.is_file():
        print(f"ERROR: no SKILL.md at {skill_md}")
        return 1

    text = skill_md.read_text(encoding="utf-8")
    parsed = split_frontmatter(text)
    if parsed is None:
        print("ERROR: no parseable frontmatter (need a `---` … `---` block at the very top)")
        return 1
    fm, body_lines = parsed

    # name
    name = fm.get("name", "")
    dir_name = skill_md.parent.name
    if not name:
        errors.append("missing required key: name")
    else:
        if not NAME_RE.match(name):
            errors.append(f"name '{name}' is not lower-case kebab-case (a-z, 0-9, single dashes)")
        if name != dir_name:
            errors.append(
                f"name '{name}' != directory '{dir_name}' "
                "(loader overrides with the dir name and warns)"
            )

    # description
    desc = fm.get("description", "")
    if not desc:
        errors.append("missing required key: description")
    else:
        if len(desc) < DESC_MIN:
            warnings.append(
                f"description is {len(desc)} chars (< {DESC_MIN}); likely too thin to trigger — "
                "add the user's actual trigger phrases"
            )
        if len(desc) > DESC_MAX:
            warnings.append(
                f"description is {len(desc)} chars (> {DESC_MAX}); risks truncation — tighten it"
            )
        if not re.search(r"(when|use (this|it)|当|使用|触发)", desc, re.IGNORECASE):
            warnings.append(
                "description reads like a feature summary, not a trigger — phrase it as "
                "\"use when …\" / \"当用户…时使用\""
            )

    # extra keys → not an error, but worth flagging (only name/description are required)
    extras = [k for k in fm if k not in ("name", "description")]
    if extras:
        warnings.append(f"non-standard frontmatter keys (ignored by the loader): {', '.join(extras)}")

    # body length
    body_count = len([ln for ln in body_lines if ln.strip()])
    if body_count > BODY_MAX_LINES:
        warnings.append(
            f"body is ~{body_count} non-blank lines (> {BODY_MAX_LINES}); "
            "split detail into reference files and point to them"
        )
    if body_count == 0:
        errors.append("body is empty — the instructions for Claude go below the frontmatter")

    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) — fix errors before testing.")
        return 1
    print(f"\nOK — frontmatter valid. {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
