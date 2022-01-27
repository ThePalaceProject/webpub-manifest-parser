# webpub manifest parser

[![Lint & Run Tests](https://github.com/ThePalaceProject/webpub-manifest-parser/actions/workflows/lint-test.yml/badge.svg)](https://github.com/ThePalaceProject/webpub-manifest-parser/actions/workflows/lint-test.yml)
[![PyPI](https://img.shields.io/pypi/v/palace-webpub-manifest-parser)](https://pypi.org/project/palace-webpub-manifest-parser/)

A parser for the [Readium Web Publication Manifest (RWPM)](https://github.com/readium/webpub-manifest), [Open Publication Distribution System 2.0 (OPDS 2.0)](https://drafts.opds.io/opds-2.0), and [Open Distribution to Libraries 1.0 (ODL)](https://drafts.opds.io/odl-1.0.html) formats.

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
- py37
- py38
- py39
- py310

For example, to run the unit test using Python 3.9 run the following command:
```bash
make test-py39
```

# Releasing

Releases will be automatically published to PyPI when new releases are created on github. We use 
`bump2version` to update the version number, then create a release in github.

To publish a new release:
- Bump the version and push it as a branch
  ```
  git checkout -b release/vX.X.X
  pip install bump2version
  bump2version {part}
  git push origin release/vX.X.X
  ```
- Create a PR for new version
- Merge PR into `main`
- Create a release for the version in github
