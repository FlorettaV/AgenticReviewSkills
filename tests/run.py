"""Tests for scripts/note.py: the check before every render, and the renderer itself.

    python3 -B tests/run.py

Every bad case is the valid fixture with one change, so each test proves one
rule. The golden note is what the valid fixture must render into; after an
intended change to the note's shape, look at the difference and regenerate it:

    python3 -B tests/run.py --regenerate
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
NOTE = HERE.parent / "scripts" / "note.py"
VALID = (HERE / "fixtures" / "valid.toml").read_text(encoding="utf-8")
GOLDEN = HERE / "fixtures" / "valid.golden.md"


def run(command: str, text: str, name: str = "mr-13-feat-currencies.toml") -> tuple[int, str, str]:
    """Run note.py on `text` in a fresh folder; return exit code, output, rendered note."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / name
        path.write_text(text, encoding="utf-8")
        done = subprocess.run([sys.executable, "-B", str(NOTE), command, str(path)],
                              capture_output=True, text=True, check=False)
        rendered = path.with_suffix(".md")
        note = rendered.read_text(encoding="utf-8") if rendered.exists() and path.suffix != ".md" else ""
        return done.returncode, done.stdout, note


def changed(old: str, new: str) -> str:
    assert VALID.count(old) == 1, old
    return VALID.replace(old, new)


# (what is wrong, the change to the valid fixture, a phrase the checker must print)
BAD = [
    ("title with three sentences",
     ('title = "We remove the upgrade step for old shops. An old shop then starts without prices"',
      'title = "We remove it. Shops break. Nobody notices"'), "3 sentences"),
    ("title with code",
     ('title = "We remove the upgrade step for old shops. An old shop then starts without prices"',
      'title = "We remove `migrate()`. An old shop then starts without prices"'), "title holds code"),
    ("title with a file",
     ('title = "We remove the upgrade step for old shops. An old shop then starts without prices"',
      'title = "We change shop/settings.py:40. An old shop then starts without prices"'), "title holds code"),
    ("banned noun in a title",
     ('title = "We write the fallback currency in three places. The next developer changes one"',
      'title = "The fallback currency drift. The next developer changes one"'), "say what happens"),
    ("citation in what_happens",
     ("We remove the step that upgraded old settings files.",
      "We remove shop/settings.py:40."), "what_happens cites a file"),
    ("missing why",
     ("why = '''\n✎ `shop/settings.py:40`", "why_not = '''\n✎ `shop/settings.py:40`"), "#1: no why"),
    ("score out of range",
     ("chance = 4\ncustomer = 4", "chance = 7\ncustomer = 4"), "is not 0–5"),
    ("unknown verdict",
     ('verdict = "block"', 'verdict = "later"'), "verdict 'later'"),
    ("high score without justify",
     (("justify = '''\nChance 4: every shop installed before version 2 still has the old key.\n"
       "Customer 4: no product can be bought.'''\n"), ""), "needs a justify"),
    ("developer finding without rule",
     ('rule = "Manageable"\n', ""), "#D2: no rule"),
    ("chance without customer on a D finding",
     ("chance = 1\ncustomer = 2\nfix_effort = 1\nverdict = \"ticket\"",
      "chance = 1\nfix_effort = 1\nverdict = \"ticket\""), "chance and customer go together"),
    ("duplicate id",
     ('id = "D2"', 'id = "1"'), "used twice"),
    ("finding for a half that did not run",
     ('halves = ["customer", "developer"]', 'halves = ["customer"]'), "developer half did not run"),
    ("developer half without rules walked",
     (('[rules_walked]\nReadable = "nothing"\nManageable = "D2"\nLinter = "nothing"\n'
       'Architecture = "nothing"\nTested = "D2"\nPayments = "nothing"\n'), ""), "[rules_walked] is empty"),
    ("a real e-mail address",
     ("An old shop's settings\nstill say", "The shop of <customer email> (anna@fake-shop-example.nl)\nstill says"),
     "e-mail address"),
    ("wrong format number",
     ("format = 2", "format = 3"), "this plugin writes format 2"),
]


class Check(unittest.TestCase):
    def test_valid_passes(self):
        code, out, _ = run("check", VALID)
        self.assertEqual(code, 0, out)
        self.assertIn("2 findings, OK", out)

    def test_bad_cases_fail(self):
        for what, (old, new), phrase in BAD:
            with self.subTest(what):
                code, out, _ = run("check", changed(old, new))
                self.assertEqual(code, 1, out)
                self.assertIn(phrase, out)

    def test_reserved_addresses_pass(self):
        text = changed("still say `currency:`", "still say `currency:` for jane+orders@example.com and a@shop.test")
        code, out, _ = run("check", text)
        self.assertEqual(code, 0, out)

    def test_older_format_is_a_notice(self):
        code, out, _ = run("check", changed("format = 2", "format = 1"))
        self.assertEqual(code, 3, out)
        self.assertIn("older than 2", out)

    def test_hand_written_note_is_a_notice(self):
        code, out, _ = run("check", "# MR 7 — `feat/x`\n\n## Findings\n", name="mr-7-feat-x.md")
        self.assertEqual(code, 3, out)
        self.assertIn("format 1", out)


class Render(unittest.TestCase):
    def test_golden(self):
        code, out, note = run("render", VALID)
        self.assertEqual(code, 0, out)
        self.assertEqual(note, GOLDEN.read_text(encoding="utf-8"),
                         "the rendered note changed; if intended, run with --regenerate and read the diff")

    def test_refuses_to_render_a_bad_note(self):
        code, out, note = run("render", changed('verdict = "block"', 'verdict = "later"'))
        self.assertEqual(code, 1, out)
        self.assertIn("nothing rendered", out)
        self.assertEqual(note, "")

    def test_customer_only_review_says_what_was_not_checked(self):
        text = VALID.split("[[finding]]\nid = \"D2\"")[0]
        text = text.replace('halves = ["customer", "developer"]', 'halves = ["customer"]')
        code, out, note = run("render", text)
        self.assertEqual(code, 0, out)
        self.assertIn("Security and GDPR not checked", note)
        self.assertIn("Not run: customer-only review.", note)


if __name__ == "__main__":
    if "--regenerate" in sys.argv:
        code, out, note = run("render", VALID)
        if code:
            sys.exit(out)
        GOLDEN.write_text(note, encoding="utf-8")
        print(f"wrote {GOLDEN.name}; read the diff before committing it")
        sys.exit(0)
    unittest.main(verbosity=1)
