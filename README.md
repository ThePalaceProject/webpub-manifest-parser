# webpub manifest parser

[![Lint & Run Tests](https://github.com/ThePalaceProject/webpub-manifest-parser/actions/workflows/lint-test.yml/badge.svg)](https://github.com/ThePalaceProject/webpub-manifest-parser/actions/workflows/lint-test.yml)

A parser for the [Readium Web Publication Manifest (RWPM)](https://github.com/readium/webpub-manifest) and [Open Publication Distribution System 2.0 (OPDS 2.0)](https://drafts.opds.io/opds-2.0) formats.

## Usage
Install the library with `pip`
```bash
pip install palace-webpub-manifest-parser
``` 

### Pyenv

You can optionally install the python version to run the library with using pyenv.

1. Install [pyenv](https://github.com/pyenv/pyenv#installation)

3. Install one of the supported Python versions:
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
pip install palace-webpub-manifest-parser
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

# Releasing

Releases will be automatically published to PyPI when new tags are pushed into the
repository. We use bump2version to update the version number and create a tag for the
release.

To publish a new release:
```
pip install bump2version
bump2version {part}
git push origin main --tags
```
