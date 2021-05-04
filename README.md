# python-webpub-manifest-parser

[![Build Status](https://travis-ci.com/vbessonov/python-webpub-manifest-parser.svg?branch=master)](https://travis-ci.com/vbessonov/python-webpub-manifest-parser)

A parser for the [Readium Web Publication Manifest (RWPM)](https://github.com/readium/webpub-manifest) and [Open Publication Distribution System 2.0 (OPDS 2.0)](https://drafts.opds.io/opds-2.0) formats.

## Usage
1. Install [pyenv](https://github.com/pyenv/pyenv#installation)

3. Install one of the supported Python versions mentioned in [.python-version](.python-version) or other PATCH versions of the same MINOR versions:
```bash
pyenv install <python-version>
```

4. Install [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv#installation) plugin

5. Create a virtual environment:
```bash
pyenv virtualenv <virtual-env-name>
pyenv activate <virtual-env-name>
```

6. Install the library
```bash
pip install webpub-manifest-parser
``` 


# Setting up a development environment

## Running tests using tox
1. Make sure that a virtual environment is not activated and deactivate it if needed:
```bash
deactivate
```

2. Install `tox` and `tox-pyenv` globally:
```bash
pip install tox tox-pyenv
```

3. Make your code prettier using isort and black:
```bash
make reformat
``` 

4. Run the linters:
```bash
make lint
```

5. To run the unit tests use the following command:
```bash
make test-<python-version>
```
where `<python-version>` is one of supported python versions:
- py27
- py36
- py37
- py38

For example, to run the unit test using Python 2.7 run the following command:
```bash
make test-py27
```