# webpub manifest parser

[![Run Tests](https://github.com/ThePalaceProject/webpub-manifest-parser/actions/workflows/test.yml/badge.svg)](https://github.com/ThePalaceProject/webpub-manifest-parser/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/palace-webpub-manifest-parser)](https://pypi.org/project/palace-webpub-manifest-parser/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
![Python: 3.8,3.9,3.10,3.11](https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)

A parser for the
[Readium Web Publication Manifest (RWPM)](https://github.com/readium/webpub-manifest),
[Open Publication Distribution System 2.0 (OPDS 2.0)](https://drafts.opds.io/opds-2.0), and
[Open Distribution to Libraries 1.0 (ODL)](https://drafts.opds.io/odl-1.0.html) formats.

## Usage

Install the library with `pip`

```bash
pip install palace-webpub-manifest-parser
```

### Pyenv

You can optionally install the python version to run the library with using pyenv.

1. Install [pyenv](https://github.com/pyenv/pyenv#installation)

2. Install one of the supported Python versions:
    ```bash
    pyenv install <python-version>
    ```

3. Install [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv#installation) plugin

4. Create a virtual environment:
    ```bash
    pyenv virtualenv <virtual-env-name>
    pyenv activate <virtual-env-name>
    ```

5. Install the library
    ```bash
    pip install palace-webpub-manifest-parser
    ```

## Setting up a development environment

### Running tests using tox

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
    pre-commit run -a
    ```

4. To run the unit tests use the following command:
    ```bash
    tox -e <python-version>
    ```
    where `<python-version>` is one of supported python versions:
   - py38
   - py39
   - py310
   - py311

    For example, to run the unit test using Python 3.9 run the following command:
    ```bash
    tox -e py39
    ```

## Releasing

Releases will be automatically published to PyPI when new releases are created on github by the
[release.yml](.github/workflows/release.yml) workflow. Just create a release in github with the version
number that you would like to use as the tag, and the rest will happen automatically.
