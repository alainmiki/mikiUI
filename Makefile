.PHONY: test lint typecheck build dev clean

test:
	python -m pytest tests/ -q --no-cov

test-cov:
	python -m pytest tests/ -q

lint:
	ruff check mikiui/ tests/

typecheck:
	mypy mikiui/

build:
	python -c "from mikiui.build.web_build import build_web; print('Build OK')"

dev:
	mikiui dev

desktop:
	mikiui desktop

clean:
	rm -rf dist/ build/ htmlcov/ .coverage .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +

install:
	pip install -e ".[dev,build,desktop,tailwind]"
