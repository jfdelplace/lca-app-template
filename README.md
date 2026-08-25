# Emissions analysis app — template

A starting point for an analysis app on the transportation-emissions platform.

**Fork this repository**, then edit `app.py`. That is the whole idea — everything else
here exists so you don't have to think about HTTP, containers, or deployment.

Forking keeps a link back to this repository, so when the client or the build gets fixed
you can pick the change up with:

```bash
git remote add upstream <this-repository-url>   # once
git pull upstream main
```

## Getting started

1. Fork this repository, and rename it for your app.
2. In `app.py`, set `APP_NAME` and `APP_DESCRIPTION`, then write your analysis.
3. Get a token from the platform: sign in, open **Developer**, section **Your API keys**,
   create one, and copy it immediately (it is shown once).
4. Run it:

```bash
pip install -r requirements.txt

export PLATFORM_API_TOKEN='the-token-you-just-copied'
export PLATFORM_API_URL='https://your-platform-address'

streamlit run app.py
```

Never commit the token. It is read from the environment for exactly that reason, and
`.gitignore` already excludes `.env`.

## The data

`platform_client.load()` returns both published resources plus the version they came from:

| | |
|---|---|
| `data.vehicle_parameters` | one row per vehicle, keyed by `(size, fuel, scenario)`. Tank-to-wheel values are `ttw_<indicator>` columns. |
| `data.emission_factors` | one row per named factor, keyed by `index`, all 16 indicators as columns. |
| `data.version` | the published version — worth stating on anything you publish. |
| `data.factor(name, indicator)` | look up one factor the way the analysis does. Raises rather than returning a silent zero. |

Field names are stable and do not change when the source spreadsheet is edited or
re-arranged. Only vehicles that actually exist are published, so you do not need to filter
placeholder rows. The full contract, generated from the platform's own code, is at
`/api/docs/` on your platform instance.

By default you get the latest published data. To reproduce a figure exactly, pin a version
with `PLATFORM_DATA_VERSION`.

## Deploying

You don't. Push to `main` (or tag a release) and CI builds and publishes the image for
you. The workflow summary prints one line:

```
ghcr.io/your-account/your-repo@sha256:...
```

Two things to hand over to whoever manages the platform:

1. That line, and your repository URL.
2. **Make the published package public**, or the platform cannot pull it. GitHub packages
   default to private: open your repository → *Packages* → the image → *Package settings* →
   *Change visibility*. If it must stay private, the platform needs a read token instead —
   ask.

The platform deploys that exact digest, so what runs is what you tested, and a rollback is
just re-deploying the previous line.
