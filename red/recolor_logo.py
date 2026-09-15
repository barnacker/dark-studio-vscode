"""Recolor VS Code's BlueStandard logo to monotonal Dark Studio red.
All three baked BlueStandard tiles map to the single DS accent red:
  #0065A9 (dark)  -> #DB0000
  #007ACC (mid)   -> #DB0000
  #1F9CF0 (light) -> #DB0000
(v1 mapped the three blues to the three-step red ladder #A1172E/#DB0000/
#E33B57; v2 collapses the ladder - one color, no tones.)

Machine-independent:
  * The canonical pre-recolor originals live in red/assets/ NEXT TO THIS
    script (tracked in the repo), so no user-specific paths are needed.
  * The VS Code app root is LOCATED AT RUNTIME, in this order:
      1. VSCODE_APP_ROOT env var (explicit override),
      2. the "code" launcher on PATH (bin/code or bin\code.cmd -> two
         levels up is the install root),
      3. the standard install locations for the current platform.
    The first candidate that actually contains a patchable icon wins.

Originals are preserved at <patched-file>.bak-ds. If a .bak-ds is missing
(e.g. vscode-icon.svg in the current build), the canonical original in
red/assets/ is used to restore before re-patching. Re-runs are idempotent:
the old ladder reds are also remapped to #DB0000, so a previously-patched
tree converges without a backup.

Re-run after a VS Code update (self-update replaces the resources/app
build dir and writes the original blue icons back). Use --dry-run to
preview what would change without writing anything.
"""
import os, re, shutil, sys
import xml.etree.ElementTree as ET

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
KEEP = {
    "code-icon.svg":   os.path.join(ASSETS, "code-icon.bak.svg"),
    "vscode-icon.svg": os.path.join(ASSETS, "vscode-icon.bak.svg"),
}
TARGET = "#DB0000"
ICONS = ("code-icon.svg", "vscode-icon.svg")
# source blues + the old v1 red ladder, all collapsed to the one DS accent
MAP = [
    (r'fill="#0065A9"', 'fill="%s"' % TARGET),
    (r'fill="#007ACC"', 'fill="%s"' % TARGET),
    (r'fill="#1F9CF0"', 'fill="%s"' % TARGET),
    (r'fill="#A1172E"', 'fill="%s"' % TARGET),
    (r'fill="#E33B57"', 'fill="%s"' % TARGET),
]

def app_root_candidates():
    """Yield candidate VS Code install roots, most specific first."""
    env = os.environ.get("VSCODE_APP_ROOT")
    if env:
        yield os.path.expanduser(env)
    # "code" launcher on PATH: <root>/bin/code(.cmd|.exe) -> root is two up.
    roots, seen = [], set()

    def add(p):
        p = os.path.abspath(p)
        if p not in seen:
            seen.add(p)
            roots.append(p)
    launcher = os.path.join(os.sep, "code")  # sentinel, replaced below
    for part in os.environ.get("PATH", "").split(os.pathsep):
        part = part.strip().strip('"')
        if not part:
            continue
        for base in ("code", "code.cmd", "code.exe"):
            p = os.path.join(part, base)
            if os.path.isfile(p):
                add(os.path.dirname(os.path.dirname(p)))
                break
    for r in roots:
        yield r
    # standard install locations
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
        yield os.path.join(local, "Programs", "Microsoft VS Code")
        yield os.path.join(local, "Programs", "Microsoft VS Code Insiders")
        yield r"C:\Program Files\Microsoft VS Code"
        yield r"C:\Program Files (x86)\Microsoft VS Code"
    elif sys.platform == "darwin":
        yield "/Applications/Visual Studio Code.app"
        yield "/Applications/Visual Studio Code - Insiders.app"
    else:
        yield os.path.join(home, ".vscode")
        yield os.path.join(home, ".vscode-insiders")
        yield "/usr/share/code"
        yield "/opt/visual-studio-code"


def find_icons(approot):
    """All patchable brand icons under approot (github-auth copies excluded)."""
    if not os.path.isdir(approot):
        return []
    found = []
    for root, _dirs, files in os.walk(approot):
        low = root.lower().replace(os.sep, "/")
        if ".bak" in low or "github-authentication" in low:
            continue
        for name in ICONS:
            if name in files:
                found.append(os.path.join(root, name))
    return found


def main():
    dry = "--dry-run" in sys.argv
    for name, keep in KEEP.items():
        if not os.path.isfile(keep):
            sys.exit("canonical original missing (repo asset) for " + name + ": " + keep)
    approot, found = None, []
    for cand in app_root_candidates():
        found = find_icons(cand)
        if found:
            approot = cand
            break
    if not approot:
        sys.exit("no " + ICONS[0] + " found on this machine. VS Code may be "
                 "mid-self-update (build dir in flux); re-run later, or point "
                 "VSCODE_APP_ROOT at the install dir containing resources/app.")
    print("app root: " + approot)
    print("icons:    " + str(len(found)))
    for f in found:
        if dry:
            print("  (dry-run) " + f)
            continue
        bak = f + ".bak-ds"
        if not os.path.exists(bak):
            # no local backup: restore from the canonical original
            shutil.copy2(KEEP[os.path.basename(f)], f)
            shutil.copy2(f, bak)
        else:
            shutil.copy2(bak, f)   # restore exact original, re-patch
        data = open(f, encoding="utf-8", newline="").read()
        new, hits = data, 0
        for pat, rep in MAP:
            new, n = re.subn(pat, rep, new)
            hits += n
        with open(f, "w", encoding="utf-8", newline="") as fh:
            fh.write(new)
        print("  %s -> %d tiles -> monotonal %s" % (f, hits, TARGET))
    if dry:
        return
    # verify: no blue left, no ladder red left, exactly the three monotonal
    # tiles per file, structure intact, well-formed XML
    for f in found:
        d = open(f, encoding="utf-8", newline="").read()
        blues = re.findall(r'fill="#00[679][0-9A-Fa-f]{3}"', d)
        ladder = re.findall(r'fill="#(?:A1172E|E33B57)"', d)
        target = re.findall(r'fill="' + TARGET + '"', d)
        assert not blues, (f, blues)
        assert not ladder, (f, ladder)
        assert len(target) == 3, (f, "expected 3 monotonal tiles, got", len(target))
        assert "evenodd" in d, (f, "structure lost")
        ET.fromstring(d)  # well-formed XML
    print("ALL %d files monotonal %s; originals in .bak-ds + red/assets/"
          % (len(found), TARGET))


if __name__ == "__main__":
    main()
