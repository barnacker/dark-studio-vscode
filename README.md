# dark-studio-vscode

Dark Studio color theme for Visual Studio Code.

Built from the Dark Studio palette (`Dark_Studio.obt`), structurally a recolor
of the stock Dark Modern / Dark+ theme set (333 color tokens, 47 token colors,
24 semantic token colors, fully self-contained — no `include`).

## Install (VSIX)

```
code --install-extension ./dark-studio-1.0.1.vsix
```

or from VS Code: `Ctrl+Shift+P` → *Install from VSIX…*.

Then `Ctrl+K Ctrl+T` → **Dark Studio**.

## Rebuild

Requires Node 18+. From this folder:

```
npx -y @vscode/vsce package --skip-license
```

Theme source of truth: `themes/dark_studio.json`.

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
