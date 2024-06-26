.PHONY: clean deepclean install dev mypy ruff ruff-format toml-sort lint pre-commit test-run test build publish doc-autobuild doc-gen doc-mypy doc-coverage doc

########################################################################################
# Variables
########################################################################################

# Documentation target directory, will be adapted to specific folder for readthedocs.
PUBLIC_DIR := $(shell [ "$$READTHEDOCS" = "True" ] && echo "$${READTHEDOCS_OUTPUT}html" || echo "public")

########################################################################################
# Development Environment Management
########################################################################################

# Remove common intermediate files.
clean:
	-rm -rf \
		$(PUBLIC_DIR) \
		.coverage \
		.mypy_cache \
		.pdm-build \
		.pdm-python \
		.pytest_cache \
		.ruff_cache \
		Pipfile* \
		__pypackages__ \
		build \
		coverage.xml \
		dist
	find . -name '*.egg-info' -print0 | xargs -0 rm -rf
	find . -name '*.pyc' -print0 | xargs -0 rm -f
	find . -name '*.swp' -print0 | xargs -0 rm -f
	find . -name '.DS_Store' -print0 | xargs -0 rm -f
	find . -name '__pycache__' -print0 | xargs -0 rm -rf

# Remove pre-commit hook, virtual environment alongside itermediate files.
deepclean: clean
	if command -v pre-commit > /dev/null 2>&1; then pre-commit uninstall; fi
	if command -v pdm >/dev/null 2>&1 && pdm venv list | grep -q in-project ; then pdm venv remove --yes in-project >/dev/null 2>&1; fi

# Install the package in editable mode.
install:
	pdm install --prod

# Install the package in editable mode with specific optional dependencies.
dev-%:
	pdm install --dev --group $*

# Prepare the development environment.
# Install the pacakge in editable mode with all optional dependencies and pre-commit hoook.
dev:
	pdm install
	if [ "$(CI)" != "true" ] && command -v pre-commit > /dev/null 2>&1; then pre-commit install; fi

########################################################################################
# Lint and pre-commit
########################################################################################

# Check lint with mypy.
mypy:
	pdm run python -m mypy .

# Lint with ruff.
ruff:
	pdm run python -m ruff check .

# Format with ruff.
ruff-format:
	pdm run python -m ruff format --check .

# Check lint with toml-sort.
toml-sort:
	pdm run toml-sort --check pyproject.toml

# Check lint with all linters.
lint: mypy

# Run pre-commit with autofix against all files.
pre-commit:
	pre-commit run --all-files --hook-stage manual

########################################################################################
# Test
########################################################################################

# Clean and run test with coverage.
test-run:
	pdm run python -m coverage erase
	pdm run python -m coverage run -m pytest

# Generate coverage report for terminal and xml.
test: test-run
	pdm run python -m coverage report
	pdm run python -m coverage xml

########################################################################################
# Package
########################################################################################

# Build the package.
build:
	pdm build

# Publish the package.
publish:
	pdm publish

########################################################################################
# Documentation
########################################################################################

# Generate documentation with auto build when changes happen.
doc-autobuild:
	pdm run python -m sphinx_autobuild docs $(PUBLIC_DIR) \
		--watch README.md \
		--watch src \
		-a

# Build documentation only from src.
doc-gen:
	pdm run python -m sphinx.cmd.build docs $(PUBLIC_DIR)

# Generate mypy reports.
doc-mypy:
	pdm run python -m mypy src tests --html-report $(PUBLIC_DIR)/reports/mypy

# Generate html coverage reports with badge.
doc-coverage: test-run
	pdm run python -m coverage html -d $(PUBLIC_DIR)/reports/coverage
	pdm run bash scripts/generate-coverage-badge.sh $(PUBLIC_DIR)/_static/badges

# Generate all documentation with reports.
doc: doc-gen doc-mypy doc-coverage

########################################################################################
# End
########################################################################################
