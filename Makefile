.PHONY: init install build publish clean reformat lint test-py27 test-py36 test-py37 test-py38 test
.DEFAULT_GOAL := all

all: install lint build

POETRY_VERSION = 1.1.5

PROJECT = python-webpub-manifest-parser
PACKAGE = palace_webpub_manifest_parser

init:
	python -m pip install pip
	pip uninstall -y enum34  # This line is required for Python versions greater than 2.7 to work correctly
	python -m pip install poetry==${POETRY_VERSION}
	poetry config virtualenvs.create false

install:
	poetry install -vvv

build:
	poetry build

publish:
	make prepare
	make config
	poetry publish --build -r pypi

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

test:
	tox -e py27,py36,py37,py38