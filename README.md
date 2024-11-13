# webpub manifest parser

🚨 **ARCHIVED** 🚨: This package has been archived, and is no longer maintained. Palace Manager has been updated to
use Pydantic instead of this parsing library. See [Palace Manager](https://github.com/ThePalaceProject/circulation)
for more information.

A parser for the
[Readium Web Publication Manifest (RWPM)](https://github.com/readium/webpub-manifest),
[Open Publication Distribution System 2.0 (OPDS 2.0)](https://drafts.opds.io/opds-2.0), and
[Open Distribution to Libraries 1.0 (ODL)](https://drafts.opds.io/odl-1.0.html) formats.

**Note**: This parser varys from the OPDS 2 + ODL spec in that it allows OPDS 2 + ODL feeds to contain
non-open access acquisition links.

The spec [defines](https://drafts.opds.io/odl-1.0.html#21-opds-20) an OPDS 2 + ODL feed as:

- It must be a valid OPDS Feed as defined in [[OPDS-2](https://drafts.opds.io/odl-1.0.html#normative-references)] with
  one difference:
    - The requirement for the presence of an Acquisition Link is relaxed
    - Instead, each Publication listed in publications must either contain a licenses subcollection or an Open-Access
      Acquisition Link (http://opds-spec.org/acquisition/open-access)

The requirement that each link be an Open-Access Acquisition Link is overly restrictive, and prevents us from importing
mixed OPDS2 and OPDS2 + ODL feeds. We relax the requirement to:

- It must be a valid OPDS Feed as defined in [[OPDS-2](https://drafts.opds.io/odl-1.0.html#normative-references)] with
  one difference:
    - The requirement for the presence of an Acquisition Link is relaxed
    - Instead, each Publication listed in publications must either contain a licenses subcollection or an
      **Acquisition Link** (http://opds-spec.org/acquisition)

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
