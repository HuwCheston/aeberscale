.PHONY: install tests fix build publish publish-test

build: install
	rm -rf dist/ build/ *.egg-info
	poetry run python -m build
	poetry run twine check dist/*

publish: build
	poetry run twine upload --repository pypi dist/* --non-interactive --verbose

publish-test: build
	poetry run twine upload --repository testpypi dist/* --non-interactive --verbose

install:
	poetry lock
	poetry install --no-interaction

tests:
	poetry run flake8 aeberscale --count --select=E9,F63,F7,F82 --show-source --statistics
	poetry run pytest tests

fix:
	poetry run pre-commit install
	poetry run pre-commit run --all-files
