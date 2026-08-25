"""Reading the platform's data.

You should not need to change this file. It is the one place that knows about HTTP, so
`app.py` can be about your analysis instead. Because you forked the template, a fix here
reaches you with `git pull upstream main` — so local edits are best avoided.

The platform publishes two resources with stable field names, independent of how the
source spreadsheet happens to be laid out. Read the full contract at `/api/docs/` on your
platform instance.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

import pandas as pd
import requests

DEFAULT_BASE_URL = "http://localhost:8000"
TIMEOUT_SECONDS = 30
TOKEN_HELP = "the platform's Developer page, under 'Your API keys'"


class PlatformError(RuntimeError):
    """Raised with something actionable, rather than letting a stack trace surface in the
    middle of the app."""


@dataclass(frozen=True)
class Dataset:
    """Both resources, plus the data version they came from.

    Keeping the version means a figure can state which data produced it — worth recording
    in anything you publish.
    """

    emission_factors: pd.DataFrame
    vehicle_parameters: pd.DataFrame
    version: int

    def factor(self, index: str, indicator: str) -> float:
        """One emission factor by name, the way the analysis code looks it up.

        Returns 0.0 for an unknown name only after saying so loudly: a silent zero is how
        a wrong number reaches a chart unnoticed.
        """
        rows = self.emission_factors
        match = rows[rows["index"].str.strip().str.casefold() == index.strip().casefold()]
        if match.empty:
            raise PlatformError(
                f"No emission factor named {index!r}. The platform refuses to publish data "
                "missing a factor the apps need, so this usually means a typo here rather "
                "than missing data."
            )
        return float(match.iloc[0][indicator])


def _config():
    token = os.environ.get("PLATFORM_API_TOKEN")
    if not token:
        raise PlatformError(
            f"PLATFORM_API_TOKEN is not set. Create a token on {TOKEN_HELP}, and put it in "
            "your environment. Never commit it."
        )
    base = os.environ.get("PLATFORM_API_URL", DEFAULT_BASE_URL).rstrip("/")
    version = os.environ.get("PLATFORM_DATA_VERSION")
    return base, token, version


_STATUS_FALLBACKS = {
    401: f"The platform rejected your token. It may have expired — create a new one on "
    f"{TOKEN_HELP}.",
    403: "This account is not allowed to read the data API.",
    404: "The platform has no published data yet.",
}


def _get(path: str) -> dict:
    base, token, version = _config()
    query = {}
    if version:
        # Pinning is opt-in. Unset means "latest", which is what you normally want.
        query["version"] = version

    try:
        response = requests.get(
            f"{base}/api/v1/{path}",
            headers={"Authorization": f"Token {token}"},
            params=query,
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as error:
        raise PlatformError(f"Could not reach the platform at {base}: {error}") from error

    # Every failure becomes a readable message, preferring the platform's own explanation
    # when it sent one. Falling through to raise_for_status() would put a stack trace in
    # front of whoever is using the app, which is exactly what this module exists to prevent.
    if not response.ok:
        fallback = _STATUS_FALLBACKS.get(
            response.status_code,
            f"The platform returned {response.status_code} for {path}. "
            "Check PLATFORM_API_URL, and that the platform is running.",
        )
        raise PlatformError(_detail(response) or fallback)

    try:
        return response.json()
    except ValueError as error:
        raise PlatformError(
            f"The platform's reply for {path} was not JSON. This usually means "
            f"PLATFORM_API_URL points at something other than the platform ({base})."
        ) from error


def _detail(response):
    """The platform's own explanation, when it sent one."""
    try:
        return response.json().get("detail")
    except (ValueError, AttributeError):
        return None


@lru_cache(maxsize=1)
def load() -> Dataset:
    """Fetch both resources once per process."""
    factors = _get("emission-factors")
    vehicles = _get("vehicle-parameters")

    vehicle_frame = pd.json_normalize(vehicles["results"])
    # Nested fields (e.g. tank-to-wheel values) flatten to dotted names like ttw.<indicator>;
    # replace dots with underscores so column names stay usable in expressions.
    vehicle_frame.columns = [name.replace(".", "_") for name in vehicle_frame.columns]

    return Dataset(
        emission_factors=pd.DataFrame(factors["results"]),
        vehicle_parameters=vehicle_frame,
        version=factors["version"],
    )
