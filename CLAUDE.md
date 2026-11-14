# Confident Assist

A Home Assistant custom integration, installed through HACS or the Marketplace.
The domain is `confident_assist`; all runtime code is in
`custom_components/confident_assist`. The approved design is in the project's
design page; this file holds the rules that keep the code in line with it.

## Rules

- **Providers stay behind the interfaces.** `providers/base.py` defines
  `DecisionProvider` and `FallbackProvider`. Only a provider's own module may
  import its API's package. The core uses only the types in `providers/types.py`.
- **A new provider is one module plus one registry line** in
  `providers/__init__.py`, and a label under `selector` in `strings.json` and
  every file in `translations/`.
- **Never half-act.** When the agent is not sure, the fallback gets the whole
  sentence and nothing has been done.
- **Every request costs the user money.** Tests replace every provider, so the
  suite spends nothing. Keep it that way.
- **Schemas use `probatio`**, which Home Assistant 2026.11 uses in place of
  voluptuous. Import it as `import probatio as vol`.
- **User-visible text** lives in `strings.json`, and `translations/en.json` is a
  copy of it. Every key goes in both.
- **Minimum Home Assistant version** is in `hacs.json`. Raise it together with
  the `pytest-homeassistant` pin and the conversation pins in
  `requirements-test.txt`.
- Write plain English with sentence-case headings. Code comments give the reason
  or the trap, not what the code does.

## Verifying

Use Python 3.14. Run all of this before calling work done:

```bash
uv venv -p 3.14 .venv && VIRTUAL_ENV=.venv uv pip install -r requirements-dev.txt
.venv/bin/ruff check custom_components tests
.venv/bin/ruff format --check custom_components tests
.venv/bin/mypy custom_components/confident_assist
.venv/bin/pytest --cov=custom_components.confident_assist --cov-fail-under=100
```

hassfest and the HACS action run in CI.

## Releases

A release bumps `version` in `manifest.json` in a commit named `Release x.y.z`,
then a GitHub release with the tag `x.y.z` (not only a tag).
