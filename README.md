# dark-studio-vscode

Dark Studio color theme for Visual Studio Code.

Built from the Dark Studio palette (`Dark_Studio.obt`), structurally a recolor
of the stock Dark Modern / Dark+ theme set (333 color tokens, 47 token colors,
24 semantic token colors, fully self-contained — no `include`).

## Install

The `.vsix` is not committed (gitignored). Two ways to get it installed:

**From this repo** (Node 18+):

```
git clone https://github.com/barnacker/dark-studio-vscode.git
cd dark-studio-vscode
npx -y @vscode/vsce package --skip-license
code --install-extension ./dark-studio-1.0.1.vsix
```

**From a local VSIX file**: `Ctrl+Shift+P` → *Install from VSIX…* and pick
the file.

Over an existing install, add `--force` to either path.

Activate: `Ctrl+K Ctrl+T` → **Dark Studio**.

## Rebuild

Requires Node 18+. From this folder:

```
npx -y @vscode/vsce package --skip-license
```

Theme source of truth: `themes/dark_studio.json`. Bump `version` in
`package.json` for the packaged name to track updates.

## Red icon

The theme recolors the UI; the VS Code logo itself (title bar, tab bar,
welcome page) stays stock blue. `red/recolor_logo.py` patches the bundled
`code-icon.svg` / `vscode-icon.svg` so all three icon tiles carry the single
Dark Studio accent red `#DB0000`.

This step is separate from the theme VSIX — it writes inside the VS Code
install directory (`resources/app`) and does not travel inside the package.

- **Machine-independent**: the script locates the VS Code install root at
  runtime (env `VSCODE_APP_ROOT` → `code` launcher on PATH → standard install
  locations for the platform). Canonical pre-recolor originals live in
  `red/assets/`, so it runs straight from a fresh clone with no user-specific
  paths.
- **Idempotent**: re-runs converge. Previously patched tiles are restored
  from the local `.bak-ds` backup (or the repo originals when absent) and
  re-patched. Originals are preserved at `<patched-file>.bak-ds` plus
  `red/assets/`.
- **Re-run after every VS Code self-update** — the update replaces the app
  build dir and writes the blue icons back. `--dry-run` previews without
  writing anything.

```
python red/recolor_logo.py            # applies the red icon
python red/recolor_logo.py --dry-run  # preview only
```

Reload VS Code (*Developer: Reload Window*) to see the icon change.

## Notable mappings

| surface | token(s) | value |
| --- | --- | --- |
| chat/center | `editor.background` | `#00040B` |
| sidebar | `sideBar.background` | `#0A0806` |
| foreground (text, icons) | `foreground` family | `#FF8300` |
| menus / dropdowns (DS "popover") | `menu.background` / `menu.selectionBackground` / `menu.borderColor` | `#12100B` / `#141109` / `#300F00` |
| chrome borders (transparent) | `activityBar.border`, `sideBar.border`, `sideBarTitle.border`, `editorGroup.border`, `sideBarSectionHeader.border`, `surface.border` | `#00000000` |
| resize sash — hover / drag | `sash.hoverBorder`, `sash.activeBorder` | `#FF8300` |

Note: `surface.border` is the modern-UI card frame around each pane (not in
the public theme-color doc; defaults to ~10% of the foreground when unset,
which shows as a brown frame on this theme). All color values are strict
`#RRGGBB` / `#RRGGBBAA`.
