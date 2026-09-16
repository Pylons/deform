# AGENTS.md — deform

Run these checks before considering work done. They mirror `.github/workflows/ci-tests.yml`
(invoked via `tox`). All commands run from the repo root.

## Fast pre-check (run first)

```sh
ruff check                  # line-length 79, excludes docs (config in pyproject.toml)
```

## Lint (CI: `tox -e lint`)

```sh
flake8 deform setup.py
isort --check-only --df deform setup.py
black --check --diff deform setup.py
python setup.py check -s -m
rstcheck README.rst CHANGES.txt
check-manifest
```

- `black` / `isort` / `flake8` line-length: **79** (see `pyproject.toml` `[tool.black]`, `[tool.isort]`).
- `flake8` ignores `E203, E731, W503` and excludes `docs` (see `.flake8`).

## Tests (CI: `tox -e py [--cov]`)

```sh
pytest                      # deform/tests, -W always (see setup.cfg [tool:pytest])
pytest --cov                # coverage (CI runs this on ubuntu-latest)
```

## Coverage gate (CI: `tox -e py311-cover,coverage`)

```sh
pytest --cov
coverage report --show-missing --fail-under=100
```

## Docs (CI: `tox -e docs`)

```sh
make -C docs html epub BUILDDIR=<builddir> "SPHINXOPTS=-W -E"   # -W = warnings as errors
```

CI reinstalls deform from source (`pip install deform[docs]`) so autodoc reads the current
source tree. If reusing a pre-existing `docs` tox env, either recreate it or prepend the
source so autodoc does not read a stale installed copy:

```sh
PYTHONPATH=<repo-root> python -m sphinx -b html -E -W -d docs/_build/doctrees docs docs/_build/html
```

## Functional / Selenium (CI: `tox -e functional3`)

Requires Firefox + geckodriver and a running Selenium standalone-firefox (`DISPLAY=:99`,
port 4444). Runs `run-selenium-tests.bash`, which clones `deformdemo` into
`deformdemo_functional_tests/`, compiles locales (`i18n.sh`), reinstalls deform, serves
`demo.ini`, then runs `pytest`. Skip unless working on functional tests.

## Notes

- Supported Python: 3.10–3.14 + PyPy 3.10 (see CI matrix).
- `deform.js` is vanilla JS (no jQuery); do not re-introduce jQuery dependencies.
