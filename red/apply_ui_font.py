"""Apply the Dark Studio UI font to VS Code's workbench chrome.

VSCode has no theme token for the UI font: the entire chrome (menus, tabs,
panels, status bar, quick opens) inherits the CSS var --monaco-monospace-font,
which the app ships platform-hardcoded in workbench.desktop.main.css:

  .monaco-workbench.windows { --monaco-monospace-font: Consolas, "Courier New", monospace }

Appending a same-specificity rule at the END of the file wins (source order),
so the UI renders in VictorMono NFP (proportional; the editor keeps NFM via
editor.fontFamily, the terminal via terminal.integrated.fontFamily).

Idempotent: a marker delimits the block; re-running replaces it in place.
Removable: `python apply_ui_font.py --remove` deletes the block, restoring
the original CSS byte-for-byte.
Re-run after a VS Code update (self-update rotates the resources/app build dir).
"""
import os, re, sys

REMOVE_FLAG = '--remove' in sys.argv[1:]
APPROOT = 'C:/Users/barn/AppData/Local/Programs/Microsoft VS Code'
MARK = '/* dark-studio ui-font */'
BLOCK = (
    MARK + '\n'
    '.monaco-workbench.windows { --monaco-monospace-font: "VictorMono NFP", '
    '"VictorMono Nerd Font Propo", Consolas, "Courier New", monospace; }\n'
)
# marker plus the whole appended block up to the next blank line or EOF
REMOVE = re.compile(re.escape(MARK) + r'.*?\n(?:.*\n)*?(?=\n|\Z)', re.MULTILINE)

files = []
for root, dirs, names in os.walk(APPROOT):
    rd = root.replace('\\', '/')
    if '/resources/app' not in rd and not rd.endswith('/resources/app'):
        continue
    if '/extensions/' in rd:
        continue
    for name in ('workbench.desktop.main.css', 'sessions.desktop.main.css'):
        p = os.path.join(root, name)
        if os.path.exists(p):
            files.append(p)

if not files:
    sys.exit('no workbench CSS found (VS Code build dir in flux? re-run after update settles)')

changed = 0
for p in files:
    data = open(p, encoding='utf-8', newline='').read()
    if MARK not in data:
        if REMOVE_FLAG:
            print(f'{p} -> clean (no ui-font block)')
            continue
        new = data.rstrip('\n') + '\n' + BLOCK
        action = 'appended'
    elif REMOVE_FLAG:
        new = REMOVE.sub('', data, count=1)
        if MARK in new:
            sys.exit(f'internal error: removal left target text in {p}')
        action = 'removed'
    else:
        # replace: strip the current block, re-append fresh
        data = REMOVE.sub('', data, count=1)
        if MARK in data:
            sys.exit(f'internal error: removal left target text in {p}')
        new = data.rstrip('\n') + '\n' + BLOCK
        action = 'replaced'
    open(p, 'w', encoding='utf-8', newline='').write(new)
    changed += 1
    print(f'{p} -> {action} ui-font block')

if changed:
    verb = 'removed' if REMOVE_FLAG else 'applied'
    print(f'ALL {len(files)} CSS files checked, {changed} {verb}. Full VSCode restart to see it.')
else:
    print('nothing to do')
