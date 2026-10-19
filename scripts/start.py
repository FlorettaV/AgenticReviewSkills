"""The start check every review skill runs before it reads the project.

    python3 -B <plugin>/scripts/start.py check [<project>]
    python3 -B <plugin>/scripts/start.py settings <review-store>

`check` answers four questions, one `key: value` line each, and a `problem:`
line for everything that stops a review:

- config:         where the review store is (~/.config/review-skills/config.toml)
- project:        the git repository under review (the current folder by default)
- review-records: the project's folder in the review store, matched by remote,
                  then path
- protection:     whether this Claude session loaded the plugin's deny rules,
                  or the operator's own settings file

It cannot test the permission system itself: a script runs outside it. When
the plugin's rules are loaded, it ends with `next: run review-guard-canary`,
and Claude runs that command to prove they are live.

`settings` writes <review-store>/review-settings.json, for `claude --settings`:
the plugin's deny rules, the review store as a folder Claude may read and write
without asking, this check as a command it may run without asking, and PIN_CWD,
so a `cd` never moves the deny rule on edits. It adds what is missing and keeps
everything else.

Exit codes: 0 ready, 1 a problem stops the review, 2 usage.
"""
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
DENY = HERE.parent / "reference" / "deny.json"
CANARY = "review-guard-canary"
# The plugin folder changes with every version, so the rule matches any of them.
START_CHECK = "Bash(python3 -B */scripts/start.py check*)"
# `Edit(./**)` is read against the shell's current folder, and a `cd` into the
# review store (an additional directory) carries over to later commands. The
# deny rule then covers the review store instead of the project, and wins over
# the allow rule there. With this set, every command starts in the project.
PIN_CWD = ("CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR", "1")


def config_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "review-skills" / "config.toml"


def plugin_rules() -> list[str]:
    return json.loads(DENY.read_text(encoding="utf-8"))["permissions"]["deny"]


# --- which settings this Claude session loaded ---------------------------

def parent(pid: int) -> tuple[int, list[str], str]:
    """The parent pid, the command line and the working folder of `pid`."""
    proc = Path(f"/proc/{pid}")
    if proc.exists():
        stat = (proc / "stat").read_text()
        ppid = int(stat[stat.rindex(")") + 2:].split()[1])
        args = (proc / "cmdline").read_bytes().split(b"\0")
        try:
            cwd = os.readlink(proc / "cwd")
        except OSError:
            cwd = ""
        return ppid, [a.decode(errors="replace") for a in args if a], cwd
    # No /proc (macOS): ps joins the arguments with spaces, so a path holding a
    # space comes out split.
    out = subprocess.run(["ps", "-o", "ppid=,command=", "-p", str(pid)],
                         capture_output=True, text=True, check=False).stdout.strip()
    if not out:
        return 0, [], ""
    ppid, _, command = out.partition(" ")
    lsof = subprocess.run(["lsof", "-a", "-d", "cwd", "-p", str(pid), "-Fn"],
                          capture_output=True, text=True, check=False).stdout
    cwd = next((line[1:] for line in lsof.splitlines() if line.startswith("n")), "")
    return int(ppid), command.split(), cwd


def is_claude(args: list[str]) -> bool:
    return bool(args) and (Path(args[0]).name == "claude"
                           or any("claude-code" in a for a in args[:2]))


def claude_process() -> tuple[list[str], str] | None:
    """The command line and start folder of the Claude session running this."""
    pid = os.getppid()
    while pid > 1:
        ppid, args, cwd = parent(pid)
        if is_claude(args):
            return args, cwd
        pid = ppid
    return None


def settings_flags(args: list[str]) -> list[str]:
    """Every value given to --settings, file or inline JSON, in order."""
    found = []
    for i, arg in enumerate(args):
        if arg == "--settings" and i + 1 < len(args):
            found.append(args[i + 1])
        elif arg.startswith("--settings="):
            found.append(arg.split("=", 1)[1])
    return found


def loaded_sources(args: list[str], cwd: str) -> list[tuple[str, dict]]:
    """(label, settings) for every settings source this session loaded."""
    sources: list[tuple[str, dict | None]] = []
    for value in settings_flags(args):
        if value.lstrip().startswith("{"):
            sources.append(("--settings <inline JSON>", parse(value)))
        else:
            path = Path(value).expanduser()
            if not path.is_absolute():
                path = Path(cwd) / path
            sources.append((f"--settings {path}", read_json(path)))
    for path in (Path.home() / ".claude" / "settings.json",
                 Path(cwd) / ".claude" / "settings.json",
                 Path(cwd) / ".claude" / "settings.local.json",
                 Path("/etc/claude-code/managed-settings.json"),
                 Path("/Library/Application Support/ClaudeCode/managed-settings.json")):
        if path.exists():
            sources.append((str(path), read_json(path)))
    return [(label, data) for label, data in sources if data is not None]


def parse(text: str) -> dict | None:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def read_json(path: Path) -> dict | None:
    try:
        return parse(path.read_text(encoding="utf-8"))
    except OSError:
        return None


def deny_rules(data: dict) -> list[str]:
    rules = data.get("permissions", {}).get("deny", [])
    return [r for r in rules if isinstance(r, str)]


def missing(sources: list[tuple[str, dict]], wanted: list[str]) -> list[str]:
    have = {rule for _, data in sources for rule in deny_rules(data)}
    gaps = [rule for rule in wanted if rule not in have]
    key, value = PIN_CWD
    if not any(str(data.get("env", {}).get(key)) == value for _, data in sources):
        gaps.append(f"env {key}={value}")
    return gaps


# --- the project and its records -----------------------------------------

def git(project: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(project), *args],
                          capture_output=True, text=True, check=False)
    return done.stdout.strip() if done.returncode == 0 else ""


def remote_key(url: str) -> str:
    """host/path, the same for the ssh and https form of one remote."""
    url = re.sub(r"^\w+://([^@/]+@)?", "", url.strip())
    url = re.sub(r"^[^@/]+@", "", url)
    url = url.replace(":", "/", 1) if re.match(r"^[^/]+:(?!\d)", url) else url
    return re.sub(r"(\.git)?/*$", "", url).lower()


ENV_LINE = re.compile(r"\*\*(Path|Remote):\*\*\s*`([^`]+)`")


def records_for(store: Path, project: Path, remote: str) -> list[Path]:
    """The review-store folders whose ENV.md names this project: by remote, else by path."""
    by_remote, by_path = [], []
    for env in sorted(store.glob("*/ENV.md")):
        fields = dict(ENV_LINE.findall(env.read_text(encoding="utf-8")))
        if remote and remote_key(fields.get("Remote", "")) == remote_key(remote):
            by_remote.append(env.parent)
        elif Path(fields.get("Path", "/nonexistent")).expanduser() == project:
            by_path.append(env.parent)
    return by_remote or by_path


def inside(path: Path, folder: Path) -> bool:
    return path == folder or folder in path.parents


# --- the commands --------------------------------------------------------

def check(project_arg: str | None) -> int:
    problems: list[str] = []

    def say(key: str, value: str) -> None:
        print(f"{key + ':':<16}{value}")

    cfg_file = config_path()
    config: dict = {}
    if cfg_file.exists():
        config = tomllib.loads(cfg_file.read_text(encoding="utf-8"))
        say("config", str(cfg_file))
    else:
        say("config", f"none yet ({cfg_file})")
        problems.append("no review store chosen yet: review-setup asks for one")
    store = Path(config["review_store"]).expanduser() if config.get("review_store") else None
    if store:
        say("review-store", str(store) + ("" if store.is_dir() else " (missing)"))
        if not store.is_dir():
            problems.append(f"the review store {store} does not exist")

    project = Path(project_arg or ".").expanduser().resolve()
    top = git(project, "rev-parse", "--show-toplevel")
    remote = ""
    if top:
        project = Path(top)
        remote = git(project, "remote", "get-url", "origin")
        say("project", f"{project}" + (f" (origin {remote})" if remote else " (no origin)"))
    else:
        say("project", f"{project} (not a git repository)")
        problems.append(f"{project} is not a git repository: the review skills review branches")

    if store and store.is_dir() and top:
        found = records_for(store, project, remote)
        if len(found) == 1:
            say("review-records", str(found[0]))
        elif found:
            say("review-records", ", ".join(map(str, found)))
            problems.append("more than one review-records folder names this project: ask which one")
        else:
            say("review-records", "none yet")
            problems.append("no records for this project yet: review-setup makes them")

    claude = claude_process()
    if claude is None:
        say("protection", "unknown: no Claude process found above this shell")
        problems.append("cannot tell which settings this session loaded")
        return finish(problems)
    args, cwd = claude
    sources = loaded_sources(args, cwd)
    flags = settings_flags(args)
    say("started", f"in {cwd}, " + (f"with --settings {', '.join(flags)}" if flags else "without --settings"))
    if top and cwd and not inside(project, Path(cwd)):
        problems.append(f"Claude was started in {cwd}, outside {project}: the deny rules on "
                        "edits only cover the start folder. Start Claude in the project")

    own = config.get("own_settings", "")
    if config.get("protection") == "own" and own:
        own_path = Path(own).expanduser()
        hit = [label for label, _ in sources if label.endswith(str(own_path))]
        if hit:
            gaps = missing([s for s in sources if s[0] in hit], plugin_rules())
            gaps = [g for g in gaps if CANARY not in g]
            say("protection", f"own settings, {own_path}")
            for gap in gaps:
                say("gap", f"{gap} is not set there" if gap.startswith("env ")
                    else f"{gap} is not denied there")
        else:
            say("protection", f"own settings {own_path}, but this session did not load it")
            problems.append(f"start Claude with --settings {own_path}")
    else:
        gaps = missing(sources, plugin_rules())
        if not gaps:
            say("protection", "plugin rules, all loaded")
            say("next", f"run `{CANARY}`; Claude Code must refuse it")
        elif len(gaps) > len(plugin_rules()):
            say("protection", "none: the plugin's deny rules are not loaded")
            settings = (store or Path("<review-store>")) / "review-settings.json"
            problems.append(f"start Claude with --settings {settings}")
        else:
            say("protection", f"plugin rules, {len(gaps)} missing")
            for gap in gaps:
                say("gap", gap)
            problems.append(f"the settings file is older than the plugin: `start.py settings {store or '<review-store>'}` "
                            "adds what is missing")
    return finish(problems)


def finish(problems: list[str]) -> int:
    for problem in problems:
        print(f"{'problem:':<16}{problem}")
    return 1 if problems else 0


def write_settings(store_arg: str) -> int:
    store = Path(store_arg).expanduser().resolve()
    path = store / "review-settings.json"
    data = read_json(path) if path.exists() else {}
    if data is None:
        print(f"{path} is not valid JSON; nothing written")
        return 1
    permissions = data.setdefault("permissions", {})
    added = []
    # A file outside the start folder is readable without asking once it is an
    # additional directory, but an edit still asks: the allow rule covers that.
    # Auto mode may block the start check as unusual; an allow rule settles it.
    # `//` starts an absolute path in a permission rule.
    for key, wanted in (("deny", plugin_rules()),
                        ("allow", [f"Edit(/{store}/**)", START_CHECK]),
                        ("additionalDirectories", [str(store)])):
        have = permissions.setdefault(key, [])
        new = [item for item in wanted if item not in have]
        have.extend(new)
        added += new
    key, value = PIN_CWD
    env = data.setdefault("env", {})
    if env.get(key) != value:
        env[key] = value
        added.append(f"env {key}={value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"{path}: {len(added)} rules added" if added else f"{path}: already up to date")
    for rule in added:
        print(f"  + {rule}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "check" and len(argv) <= 3:
        return check(argv[2] if len(argv) == 3 else None)
    if len(argv) == 3 and argv[1] == "settings":
        return write_settings(argv[2])
    print(__doc__.split("\n\n")[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
