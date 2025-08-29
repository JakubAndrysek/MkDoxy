.PHONY: package release release-test clean reviewCode docs-serve docs-build

# Packaging
package:
	rm -f dist/*
	hatch build

install: package
	hatch install

release: package
	hatch publish

release-test: package
	hatch publish --index test

clean:
	rm -rf dist build
	hatch clean


# Testing
reviewCode:
	sourcery review mkdoxy --in-place

install-dev:
	hatch env create

# Documentation
docs-serve:
	mkdocs serve --strict

docs-build: # results in site directory
	mkdocs build

pre-commit:
	pre-commit run --show-diff-on-failure --color=always --all-files

# Linting
lint:
	ruff check mkdoxy

format:
	ruff format mkdoxy

lint-fix:
	ruff check --fix mkdoxy
