# Emissions analysis app — template

A starting point for an analysis app on the transportation-emissions platform.

**Start your own private repository from this one**, then edit `app.py`. That is the
whole idea — everything else here exists so you don't have to think about HTTP,
containers, or deployment. Don't use GitHub's Fork button: a fork of a public repository
is always public, and your app's code and image should not be.

```bash
git clone --depth 1 <this-repository-url> your-app-name
cd your-app-name && rm -rf .git && git init -b main
git add -A && git commit -m "Start from the app template"
gh repo create your-account/your-app-name --private --source=. --remote=origin --push
git remote add upstream <this-repository-url>   # so a template fix can still reach you

# later, to pick up a fix to platform_client.py or app.py's surrounding scaffolding:
git pull upstream main
```

(No `gh`? Create the private repository on GitHub yourself, then `git remote add origin
<its URL> && git push -u origin main` instead of the `gh repo create` line.) Keeping the
`upstream` remote is the same benefit a GitHub fork would have given you — "please copy
this file" becomes a one-line pull — without making your repository public to get it.

## Getting started

1. Start your own private repository from this one (above), and rename it for your app.
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
2. **Grant the platform's GHCR identity read access to your package** — its GitHub page →
   *Package settings* → *Manage Actions access* (or add it as a collaborator with Read).
   Ask your admin for the exact identity (`GHCR_USERNAME`), shown to you on `/developer/`
   when you signed in. Your repository and its image stay private; this is the only thing
   the platform needs.

The platform deploys that exact digest, so what runs is what you tested, and a rollback is
just re-deploying the previous line.
