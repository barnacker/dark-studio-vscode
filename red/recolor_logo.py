"""Recolor VS Code's BlueStandard logo to monotonal Dark Studio red.
All three baked BlueStandard tiles map to the single DS accent red:
  #0065A9 (dark)  -> #DB0000
  #007ACC (mid)   -> #DB0000
  #1F9CF0 (light) -> #DB0000
(v1 mapped the three blues to the three-step red ladder #A1172E/#DB0000/
#E33B57; v2 collapses the ladder — one color, no tones.)
Originals are preserved at <app>/out/.../<file>.bak-ds. If a .bak-ds is
missing (e.g. vscode-icon.svg in the current build), the canonical original
in red/assets/ is used to restore before re-patching. Re-runs are idempotent:
the old ladder reds are also remapped to #DB0000, so a previously-patched
tree converges without a backup.
Re-run after a VS Code update (self-update rotates the resources/app build dir).
"""
import os, re, shutil, sys
import xml.etree.ElementTree as ET

APPROOT = 'C:/Users/barn/AppData/Local/Programs/Microsoft VS Code'
ASSETS = 'C:/Users/barn/Desktop/dark_studio_vscode/red/assets'
KEEP = {
    'code-icon.svg':   os.path.join(ASSETS, 'code-icon.bak.svg'),
    'vscode-icon.svg': os.path.join(ASSETS, 'vscode-icon.bak.svg'),
}
TARGET = '#DB0000'

found = []
for root, dirs, files in os.walk(APPROOT):
    for name in ('code-icon.svg', 'vscode-icon.svg'):
        if name in files and '.bak' not in root.replace('\\', '/'):
            # skip the GitHub-auth extension's brand asset - that logo is GitHub's, not ours
            if 'github-authentication' in root.replace('\\', '/'):
                continue
            found.append(os.path.join(root, name))

if not found:
    sys.exit('no code-icon.svg found (VS Code build dir in flux? re-run after update settles)')

# source blues + the old v1 red ladder, all collapsed to the one DS accent
MAP = [
    (r'fill="#0065A9"', f'fill="{TARGET}"'),
    (r'fill="#007ACC"', f'fill="{TARGET}"'),
    (r'fill="#1F9CF0"', f'fill="{TARGET}"'),
    (r'fill="#A1172E"', f'fill="{TARGET}"'),
    (r'fill="#E33B57"', f'fill="{TARGET}"'),
]

for f in found:
    name = os.path.basename(f)
    bak = f + '.bak-ds'
    if not os.path.exists(bak):
        # no local backup; restore from the canonical original and save the backup
        src = KEEP.get(name)
        if not os.path.exists(src):
            sys.exit(f'no .bak-ds and no canonical original for {f} - refusing to guess')
        shutil.copy2(src, f)
        shutil.copy2(f, bak)
    else:
        shutil.copy2(bak, f)   # restore exact original, re-patch
    data = open(f, encoding='utf-8', newline='').read()
    new, hits = data, 0
    for pat, rep in MAP:
        new, n = re.subn(pat, rep, new)
        hits += n
    open(f, 'w', encoding='utf-8', newline='').write(new)
    print(f'{f} -> {hits} tiles -> monotonal {TARGET}')

# verify: no blue left, no ladder red left, exactly the three monotonal fills, valid XML
for f in found:
    d = open(f, encoding='utf-8', newline='').read()
    blues  = re.findall(r'fill="#00[679][0-9A-Fa-f]{3}"', d)
    ladder = re.findall(r'fill="#(?:A1172E|E33B57)"', d)
    target = re.findall(rf'fill="{TARGET}"', d)
    assert not blues, (f, blues)
    assert not ladder, (f, ladder)
    assert len(target) == 3, (f, 'expected 3 monotonal tiles, got', len(target))
    assert d.count('evenodd') > 0, 'structure lost'
    ET.fromstring(d)          # well-formed XML
print(f'ALL {len(found)} files monotonal {TARGET}; originals in .bak-ds + red/assets/')
