# Installation

MikiUI can be installed from PyPI or from source.

## From PyPI (recommended)

```bash
pip install mikiui
```

### Optional extras

```bash
# Tailwind CSS support
pip install mikiui[tailwind]
npm install  # installs Tailwind + DaisyUI

# Desktop app support (pywebview)
pip install mikiui[desktop]

# All extras
pip install mikiui[dev,build,desktop,tailwind]
```

## From Source

```bash
git clone https://github.com/alainmiki/mikiUI.git
cd mikiUI
pip install -e ".[dev,build,desktop,tailwind]"
```

## System Requirements

- **Python 3.14 or later**
- **pip** (included with Python)
- **Node.js 18+** (only for Tailwind CSS)

## Verify Installation

```bash
mikiui --help
```

You should see the MikiUI banner with available commands.

## IDE Setup

### VS Code

Install the official MikiUI extension for component snippets, theme preview, and dev server integration.

### PyCharm / IntelliJ

No special plugin required. Just open the project folder and run `mikiui dev` from the terminal.

## Next Steps

- Read [Getting Started](../guide/getting-started.md) for your first app
- Browse [Components](../guide/components.md) and [Widgets](../guide/widgets.md)
- Learn about [Styling](../guide/styling.md) and [Themes](../guide/themes.md)
- Explore the [API Reference](../guide/api-reference.md)
