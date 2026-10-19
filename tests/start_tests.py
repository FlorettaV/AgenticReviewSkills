"""Tests for scripts/start.py, the start check. Run through tests/run.py."""
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("start", HERE.parent / "scripts" / "start.py")
start = importlib.util.module_from_spec(spec)
spec.loader.exec_module(start)


class SettingsFlags(unittest.TestCase):
    def test_both_spellings_and_inline_json(self):
        args = ["claude", "--settings", "a.json", "--continue", '--settings={"x": 1}']
        self.assertEqual(start.settings_flags(args), ["a.json", '{"x": 1}'])

    def test_none(self):
        self.assertEqual(start.settings_flags(["claude", "--continue"]), [])

    def test_relative_path_is_read_from_the_start_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, "deny.json").write_text('{"permissions": {"deny": ["Bash(x)"]}}')
            sources = start.loaded_sources(["claude", "--settings", "deny.json"], folder)
            self.assertIn(["Bash(x)"], [start.deny_rules(data) for _, data in sources])


class Missing(unittest.TestCase):
    def test_every_rule_across_all_sources_counts(self):
        rules = start.plugin_rules()
        half = len(rules) // 2
        sources = [("a", {"permissions": {"deny": rules[:half]}}),
                   ("b", {"permissions": {"deny": rules[half:]}, "env": dict([start.PIN_CWD])})]
        self.assertEqual(start.missing(sources, rules), [])

    def test_names_what_is_missing(self):
        rules = start.plugin_rules()
        sources = [("a", {"permissions": {"deny": rules[1:]}, "env": dict([start.PIN_CWD])})]
        self.assertEqual(start.missing(sources, rules), rules[:1])

    def test_a_cd_that_carries_over_is_a_gap(self):
        rules = start.plugin_rules()
        sources = [("a", {"permissions": {"deny": rules}})]
        self.assertEqual(start.missing(sources, rules), [f"env {start.PIN_CWD[0]}=1"])

    def test_the_canary_is_in_the_plugin_rules(self):
        self.assertTrue(any(start.CANARY in rule for rule in start.plugin_rules()))


class Records(unittest.TestCase):
    def test_ssh_and_https_are_one_remote(self):
        self.assertEqual(start.remote_key("git@gitlab.example.com:team/shop.git"),
                         start.remote_key("https://gitlab.example.com/team/shop/"))
        self.assertNotEqual(start.remote_key("git@host:team/shop.git"),
                            start.remote_key("git@host:team/shop-api.git"))

    def test_matched_by_remote_before_path(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Path(folder)
            for name, path, remote in (("shop", "/elsewhere/shop", "git@host:team/shop.git"),
                                       ("old", "/work/shop", "git@host:team/other.git")):
                (store / name).mkdir()
                (store / name / "ENV.md").write_text(
                    f"- **Path:** `{path}`\n- **Remote:** `{remote}`\n")
            found = start.records_for(store, Path("/work/shop"), "https://host/team/shop")
            self.assertEqual(found, [store / "shop"])
            found = start.records_for(store, Path("/work/shop"), "")
            self.assertEqual(found, [store / "old"])


class WriteSettings(unittest.TestCase):
    def test_adds_the_rules_and_keeps_the_rest(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Path(folder).resolve()
            path = store / "review-settings.json"
            path.write_text('{"model": "x", "permissions": {"deny": ["Bash(rm *)"]}}')
            with redirect_stdout(io.StringIO()):
                self.assertEqual(start.write_settings(folder), 0)
            data = json.loads(path.read_text())
            self.assertEqual(data["model"], "x")
            self.assertEqual(data["permissions"]["deny"][0], "Bash(rm *)")
            self.assertEqual(data["permissions"]["deny"][1:], start.plugin_rules())
            self.assertEqual(data["permissions"]["allow"], [f"Edit(/{store}/**)", start.START_CHECK])
            self.assertEqual(data["permissions"]["additionalDirectories"], [str(store)])
            self.assertEqual(data["env"], {start.PIN_CWD[0]: start.PIN_CWD[1]})
            out = io.StringIO()
            with redirect_stdout(out):
                start.write_settings(folder)
            self.assertIn("already up to date", out.getvalue())
