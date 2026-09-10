# Contributing to MikiUI

Thank you for your interest in contributing to MikiUI! This guide covers the development workflow, coding standards, and release process.

## Development Setup

```bash
git clone https://github.com/alainmiki/mikiUI.git
cd mikiUI
pip install -e ".[dev,build,desktop,tailwind]"
```

## Running Tests

```bash
# Unit tests
python -m pytest tests/ --ignore=tests/e2e

# With coverage
python -m pytest tests/ --cov=mikiui --cov-report=html

# Specific test file
python -m pytest tests/test_desktop.py -v
```

## Linting and Type Checking

```bash
# Lint with ruff
ruff check mikiui/ tests/

# Type check with mypy
mypy mikiui/
```

## Building Documentation

```bash
# Install docs dependencies
pip install -r requirements-docs.txt

# Build docs
mkdocs build

# Serve docs locally
mkdocs serve
```

## Project Structure

```
mikiUI/
├── mikiui/                    # Main package
│   ├── app/                   # Application core
│   ├── backend/               # FastAPI backend
│   ├── build/                 # Build system (web, desktop, tailwind)
│   ├── cli/                   # CLI commands
│   ├── components/            # Base HTML components
│   ├── engine/                # Rendering engine
│   ├── router/                # Routing and middleware
│   ├── runtime/               # Runtime JS/CSS assets
│   ├── styling/               # Theme and styling system
│   └── widgets/               # High-level widgets
├── docs/                      # Documentation source
├── tests/                     # Test suite
├── context/                   # Project context and specs
└── pyproject.toml             # Project configuration
```

## Coding Standards

- **Python 3.14+** syntax and type hints
- **ruff** for linting (line length: 120)
- **mypy** for type checking
- **pytest** for testing
- Follow existing code patterns and conventions

## Commit Messages

Follow conventional commits:

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation changes
- `style:` — formatting, missing semicolons, etc.
- `refactor:` — code refactoring
- `test:` — adding tests
- `chore:` — maintenance tasks

Example:
```
feat(build): add auto-install for PyInstaller in desktop builds
```

## Release Process

1. Update version in `pyproject.toml`
2. Update `docs/changelog.md` with release notes
3. Commit changes and push to `main`
4. Create and push a tag: `git tag v0.x.0 && git push --tags`
5. GitHub Actions will:
   - Run lint, type check, and tests
   - Build sdist and wheel
   - Create a GitHub Release
   - Publish to PyPI (requires `pypi` environment)

## Branch Strategy

- `main` — production-ready code
- `dev` — integration branch for features
- Feature branches — created from `dev`, merged back via PR

## Questions?

Open an issue or reach out on [GitHub Discussions](https://github.com/alainmiki/mikiUI/discussions).
