"""Check a review note's data file, and render it into the Markdown note people read.

    python3 -B <plugin>/scripts/note.py check  review/mr-13-feat-x.toml
    python3 -B <plugin>/scripts/note.py render review/mr-13-feat-x.toml

The .toml file is the note: every skill reads and writes it. The .md file next
to it is rendered from it for people to read, and is never edited or read back.
`render` checks first and writes nothing when the check fails.

`check` on a .md file only reports which format it is in: a note from before
the data format (format 1) can be read, but not checked or rendered.

Exit codes: 0 OK, 1 problems found, 2 usage, 3 an older format (a notice).
"""
import re
import sys
import tomllib
from pathlib import Path

FORMAT = 2
HALVES = ("customer", "developer")
VERDICTS = ("block", "ticket", "talk", "–")
CUSTOMER_SCORES = ("chance", "customer", "fix_effort")
DEVELOPER_SCORES = ("next_change", "security", "gdpr", "layers", "fix_effort")
TEXTS = ("what_happens", "why", "fix")

# Nouns that label a problem instead of saying it. The review-writing skill,
# "Do not invent a noun for the problem", is where a word gets added.
BANNED = re.compile(r"\b(asymmetr\w*|second home|drift|surface|coupling|grounded)\b", re.IGNORECASE)
# A file:line citation, which belongs in Why and the Cause column.
CITATION = re.compile(r"\b[\w./-]+\.\w{1,5}:\d+")
EMAIL = re.compile(r"\b[\w.%+-]+@([\w-]+(?:\.[\w-]+)+)\b")
RESERVED = re.compile(r"(^|\.)(example\.(com|net|org)|example|test|invalid|localhost)$", re.IGNORECASE)
STAMP = re.compile(r"<!-- review format: (\d+)")


def sentences(text: str) -> int:
    body = re.sub(r"`[^`]*`|\"[^\"]*\"", "x", text.strip().rstrip("."))
    return len(re.findall(r"[.!?](?:\s|$)", body)) + 1


def is_score(value, name: str) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return 0 <= value <= 5
    if isinstance(value, str):
        return value in ("–", "-") or (value == "?" and name == "chance") or "→" in value
    return False


def high(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 3


def problems(data: dict, raw: str) -> list[str]:
    out: list[str] = []
    if data.get("format") != FORMAT:
        out.append(f"format is {data.get('format')!r}; this plugin writes format {FORMAT}")
    mr = data.get("mr", {})
    for key in ("number", "branch", "reviewed", "head", "halves", "what_it_does"):
        if not mr.get(key):
            out.append(f"[mr] has no {key}")
    halves = mr.get("halves", [])
    for half in halves:
        if half not in HALVES:
            out.append(f"[mr] halves: {half!r} is not one of {', '.join(HALVES)}")

    seen: set[str] = set()
    for f in data.get("finding", []):
        n = str(f.get("id", "?"))
        tag = f"#{n}"
        if not re.fullmatch(r"D?\d+", n):
            out.append(f"{tag}: id must be 1, 2, … or D1, D2, …")
            continue
        if n in seen:
            out.append(f"{tag}: the id is used twice")
        seen.add(n)
        dev = n.startswith("D")
        half = "developer" if dev else "customer"
        if half not in halves:
            out.append(f"{tag}: a {half} finding, but the {half} half did not run")

        title = f.get("title", "")
        if not title:
            out.append(f"{tag}: no title")
        if sentences(title) > 2:
            out.append(f"{tag}: title has {sentences(title)} sentences (max 2)")
        if "`" in title or CITATION.search(title):
            out.append(f"{tag}: title holds code or a file; names belong in the Cause column")
        for word in BANNED.findall(title):
            out.append(f"{tag}: title uses \"{word}\"; say what happens instead")

        for key in TEXTS:
            if not str(f.get(key, "")).strip():
                out.append(f"{tag}: no {key}")
        what = str(f.get("what_happens", ""))
        for word in BANNED.findall(what):
            out.append(f"{tag}: what_happens uses \"{word}\"; say what happens instead")
        if CITATION.search(what):
            out.append(f"{tag}: what_happens cites a file; citations belong in why")

        scores = DEVELOPER_SCORES if dev else CUSTOMER_SCORES
        if dev and not f.get("rule"):
            out.append(f"{tag}: no rule")
        if dev and ("chance" in f) != ("customer" in f):
            out.append(f"{tag}: chance and customer go together")
        for key in scores + (("chance", "customer") if dev else ()):
            if key not in f:
                if key in scores:
                    out.append(f"{tag}: no {key}")
                continue
            if not is_score(f[key], key):
                out.append(f"{tag}: {key} = {f[key]!r} is not 0–5, – or a → score")
        if f.get("verdict") not in VERDICTS:
            out.append(f"{tag}: verdict {f.get('verdict')!r} is not one of {', '.join(VERDICTS)}")
        if any(high(f.get(k)) for k in scores + ("chance", "customer")) and not str(f.get("justify", "")).strip():
            out.append(f"{tag}: a score of 3 or more needs a justify sentence")

    if "developer" in halves and not data.get("rules_walked"):
        out.append("developer half ran, but [rules_walked] is empty")

    for m in EMAIL.finditer(raw):
        if not RESERVED.search(m.group(1)):
            out.append(f"e-mail address {m.group(0)!r}: replace it with <customer email> "
                       f"or a made-up one on example.com")
    return out


def cell(value) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def score(f: dict, key: str) -> str:
    value = f.get(key, "–")
    text = "–" if value == "-" else str(value)
    if isinstance(value, int) and not isinstance(value, bool):
        text += " ❗" if value >= 4 else " ⚠️" if value == 3 else ""
    if key == "verdict" and value == "block":
        text += " ❗"
    was = f.get("was", {})
    if key in was:
        text += f" (was {was[key]})"
    return text


def table(head: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(cell(c) for c in row) + " |" for row in rows]
    return lines


def columns(f: dict) -> list[tuple[str, str]]:
    if not str(f["id"]).startswith("D"):
        return [("Chance", "chance"), ("Customer", "customer"), ("Fix effort", "fix_effort"), ("Verdict", "verdict")]
    cols = [("Rule", "rule"), ("Next change", "next_change"), ("Security", "security"),
            ("GDPR", "gdpr"), ("Layers", "layers")]
    if "chance" in f:
        cols += [("Chance", "chance"), ("Customer", "customer")]
    return cols + [("Fix effort", "fix_effort"), ("Verdict", "verdict")]


def block(f: dict) -> list[str]:
    cols = columns(f)
    out = [f"### {f['id']}. {f['title']}", ""]
    out += table([c for c, _ in cols], [[f.get(k, "–") if k == "rule" else score(f, k) for _, k in cols]])
    out.append("")
    if f.get("rescored"):
        out += [f["rescored"].strip(), ""]
    out += [f"**What happens.** {f['what_happens'].strip()}", "",
            f"**Why.** {f['why'].strip()}", "",
            f"**Fix.** {f['fix'].strip()}", ""]
    if f.get("justify"):
        out += [f["justify"].strip(), ""]
    return out


def half(findings: list[dict], dev: bool) -> list[str]:
    if not findings:
        return ["No findings.", ""]
    if dev:
        head = ["✓", "#", "Finding", "Rule", "Next change", "Security", "GDPR", "Layers",
                "Fix effort", "Verdict", "Cause ✎ → Effect"]
        keys = ["rule", "next_change", "security", "gdpr", "layers", "fix_effort", "verdict"]
    else:
        head = ["✓", "#", "Finding", "Chance", "Customer", "Fix effort", "Verdict", "Cause ✎ → Effect"]
        keys = ["chance", "customer", "fix_effort", "verdict"]
    rows = [["[x]" if f.get("ticked") else "[ ]", f["id"], f["title"]]
            + [f.get(k, "–") if k == "rule" else score(f, k) for k in keys] + [f.get("cause", "")]
            for f in findings]
    return table(head, rows) + [""]


def section(title: str, text) -> list[str]:
    body = str(text).strip() if text else "Not touched."
    return [f"## {title}", "", body, ""]


def render(data: dict, source: str) -> str:
    mr = data["mr"]
    halves = mr["halves"]
    found = data.get("finding", [])
    customer = [f for f in found if not str(f["id"]).startswith("D")]
    developer = [f for f in found if str(f["id"]).startswith("D")]
    seen = [f["id"] for f in developer if "chance" in f]

    out = [(f"<!-- review format: {FORMAT}. Rendered from {source} by the review plugin; "
            f"change the .toml and render again, never this file. -->"),
           f"# MR {mr['number']} — `{mr['branch']}`", "",
           f"Reviewed {mr['reviewed']}, read-only. Base `{mr.get('base', '–')}`, head `{mr['head']}`.", ""]
    if halves == ["customer"]:
        out += ["**Security and GDPR not checked:** customer-only review.", ""]
    commits = ", ".join(re.sub(r"^(\w+) ", r"`\1` ", c) for c in mr.get("commits", []))
    out += table(["", ""], [["Commits", commits or "–"], ["Diff", mr.get("diff", "–")]]) + [""]
    if mr.get("header"):
        out += [mr["header"].strip(), ""]
    out += section("What it does", mr["what_it_does"])

    out += ["## What the customer experiences", ""]
    if "customer" in halves:
        out += half(customer, dev=False)
        if seen:
            out += [f"Also seen by customers: {', '.join(seen)}.", ""]
        for f in customer:
            out += block(f)
    else:
        out += ["Not run: developer-only review.", ""]

    out += ["## What the developer sees", ""]
    if "developer" in halves:
        out += half(developer, dev=True)
        for f in developer:
            out += block(f)
        out += ["### Rules walked", ""]
        out += [f"- **{rule}**: {what}" for rule, what in data.get("rules_walked", {}).items()] + [""]
    else:
        out += ["Not run: customer-only review.", ""]

    out += section("Verified as not a problem", mr.get("verified"))
    out += section("Architecture check", mr.get("architecture"))
    out += section("Interaction with other open MRs", mr.get("interaction"))
    out += section("Suggested disposition", mr.get("disposition"))
    out += section("Read-only check", mr.get("readonly_check"))
    commands = mr.get("commands", [])
    out += ["## Commands for the operator", "", "```", *commands, "```"] if commands else \
           section("Commands for the operator", None)
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in ("check", "render"):
        print(__doc__.strip().split("\n\n")[1])
        return 2
    path = Path(argv[2])
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        m = STAMP.search(raw)
        found = int(m.group(1)) if m else 1
        if found < FORMAT:
            print(f"{path.name}: format {found}, from before the data format. It can be read, "
                  f"not checked or rendered; start a new review for a full one.")
            return 3
        print(f"{path.name}: rendered from a data file; check that file instead.")
        return 2
    data = tomllib.loads(raw)
    if isinstance(data.get("format"), int) and data["format"] < FORMAT:
        print(f"{path.name}: format {data['format']}, older than {FORMAT}. Shown as it is; "
              f"start a new review for a full one.")
        return 3
    found = problems(data, raw)
    for p in found:
        print(p)
    n = len(data.get("finding", []))
    if found:
        print(f"{path.name}: {n} findings, {len(found)} problem(s)"
              + ("; nothing rendered" if argv[1] == "render" else ""))
        return 1
    if argv[1] == "render":
        target = path.with_suffix(".md")
        target.write_text(render(data, path.name), encoding="utf-8")
        print(f"{path.name}: {n} findings, OK; rendered {target.name}")
    else:
        print(f"{path.name}: {n} findings, OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
