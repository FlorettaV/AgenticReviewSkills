"""Check one review note against the shape and the title rules in the review-writing skill.

    python3 <review-writing skill dir>/check_note.py review/<note>.md

Reports, and exits 1 when anything is wrong:
  - a table row whose cell count differs from its header;
  - a finding title over two sentences, or holding a backtick (code names
    belong in the Cause column);
  - a finding with no `### <n>. <title>` heading, or a heading that is not the
    table's title word for word;
  - a detail block without its score row or one of What happens / Why / Fix;
  - a banned noun in a title or a What happens paragraph.

Checks the shape only. Whether the words are right is still a read.
"""
import re
import sys
from pathlib import Path

LABELS = ("**What happens.**", "**Why.**", "**Fix.**")

# Nouns that label a problem instead of saying it. The review-writing skill,
# "Do not invent a noun for the problem", is where a word gets added.
BANNED = re.compile(r"\b(asymmetr\w*|second home|drift|surface|coupling|grounded)\b", re.I)


def cells(line: str) -> int:
    # Pipes inside backticks are content, not cell borders.
    return re.sub(r"`[^`]*`", "x", line).count("|")


def sentences(title: str) -> int:
    body = re.sub(r"`[^`]*`|\"[^\"]*\"", "x", title.strip().rstrip("."))
    return len(re.findall(r"[.!?](?:\s|$)", body)) + 1


def main(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    problems: list[str] = []

    header, header_line, in_code = None, 0, False
    for i, line in enumerate(lines, 1):
        if line.startswith("```"):
            in_code = not in_code
        if in_code or not line.startswith("|"):
            header = None
            continue
        if header is None:
            header, header_line = cells(line), i
        elif cells(line) != header:
            problems.append(f"line {i}: {cells(line)} borders, header on line "
                            f"{header_line} has {header}")

    rows = {}
    for m in re.finditer(r"^\| \[.\] \| (\d+) \| ([^|]*?) \|", text, re.M):
        rows[int(m.group(1))] = m.group(2).strip()
    for n, title in rows.items():
        if sentences(title) > 2:
            problems.append(f"#{n}: title has {sentences(title)} sentences (max 2)")
        if "`" in title:
            problems.append(f"#{n}: title holds code; move names to the Cause column")
        for word in BANNED.findall(title):
            problems.append(f"#{n}: title uses \"{word}\"; say what happens instead")

    blocks = {}
    for part in re.split(r"\n(?=### \d+\. )", text)[1:]:
        m = re.match(r"### (\d+)\. (.*)", part)
        blocks[int(m.group(1))] = (m.group(2).strip(), part.split("\n## ")[0])
    for n, title in rows.items():
        if n not in blocks:
            problems.append(f"#{n}: no detail heading `### {n}. <title>`")
            continue
        heading, body = blocks[n]
        if heading != title:
            problems.append(f"#{n}: heading is not the table title word for word")
        if "| Chance |" not in body:
            problems.append(f"#{n}: no score row under the heading")
        what = re.search(r"\*\*What happens\.\*\*(.*?)(?=\*\*Why\.\*\*|$)", body, re.S)
        for word in BANNED.findall(what.group(1) if what else ""):
            problems.append(f"#{n}: What happens uses \"{word}\"; say what happens instead")
        missing = [label for label in LABELS if label not in body]
        if missing:
            problems.append(f"#{n}: missing {', '.join(missing)}")

    for p in problems:
        print(p)
    print(f"{path.name}: {len(rows)} findings, "
          f"{'OK' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
