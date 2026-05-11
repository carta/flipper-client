THRIFT_DIR=./flipper_thrift
THRIFT_PYTHON=${THRIFT_DIR}/python

.PHONY: install install-dev test lint format clean build publish thrift

install:
	uv sync

install-dev:
	uv sync --group dev

test:
	uv run pytest tests

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	@rm -rf build
	@rm -rf dist

build: clean
	uv build

publish: build
	uv publish

thrift:
	thrift -r --gen py -out ${THRIFT_PYTHON} ${THRIFT_DIR}/*.thrift

hooks:
	uv run pre-commit run --all-files

mypy:
	uv run mypy --follow-imports=silent --ignore-missing-imports flipper
