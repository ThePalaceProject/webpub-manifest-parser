.PHONY: init install build publish clean reformat lint test-py27 test-py36 test-py37 test-py38 test
.DEFAULT_GOAL := all

all: install lint build

POETRY_VERSION = 1.1.12

PROJECT = python-webpub-manifest-parser
PACKAGE = palace_webpub_manifest_parser

init:
	python -m pip install -U pip
	pip uninstall -y enum34  # This line is required for Python versions greater than 2.7 to work correctly
	python -m pip install poetry==${POETRY_VERSION}
	# poetry config virtualenvs.create false #This changes global configs

install:
	poetry install -vvv --no-root

build:
	poetry build

publish:
	poetry publish --build

clean:
	rm -rf build dist

reformat:
	tox -e isort-reformat,black-reformat

lint:
	tox -e isort,black,flake8,pylint

test-py27:
	tox -e py27

test-py36:
	tox -e py36

test-py37:
	tox -e py37

test-py38:
	tox -e py38

test-py39:
	tox -e py39

test-py310:
	tox -e py310

test:
	tox -e py27,py36,py37,py38,py39,py310
