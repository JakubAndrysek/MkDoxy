.PHONY: package release release-test clean reviewCode docs-serve docs-build

# Packaging
package:
	rm -f dist/*
	python3 -m build --wheel  # Updated to use python3 build tool for wheel
	python3 setup.py sdist

install: package
	python3 -m pip install --no-deps --force dist/*.whl

release: package
	twine upload --repository pypi dist/*

release-test: package
	twine upload --repository testpypi dist/*

clean:
	rm -rf dist build


# Testing
reviewCode:
	sourcery review mkdoxy --in-place

install-dev:
	python3 -m pip install --force --editable .

# Documentation
docs-serve:
	mkdocs serve --strict

docs-build: # results in site directory
	mkdocs build

pre-commit:
	pre-commit run --show-diff-on-failure --color=always --all-files
