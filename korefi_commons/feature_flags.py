"""Feature flag helpers for KoreFi services.

Typical usage::

    from korefi_commons.feature_flags import FeatureFlagService

    flags = FeatureFlagService()
    if flags.is_on("example-flag"):
        ...

Local development can drop a ``feature-flags.json`` file at the repository
root (ignored by Git) to bypass AWS AppConfig. In all remote environments the
file should be absent so AppConfig remains the single source of truth.
"""

from __future__ import annotations

import json
import logging
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError


logger = logging.getLogger(__name__)

DEFAULT_TTL_SECONDS = 45
DEFAULT_REGION = "ap-south-1"
DEFAULT_LOCAL_PATH = Path(__file__).resolve().parent.parent / "feature-flags.json"

APPLICATION_ENV_VAR = "KORE_FEATURE_FLAGS_APPLICATION_ID"
ENVIRONMENT_ENV_VAR = "KORE_FEATURE_FLAGS_ENVIRONMENT_ID"
PROFILE_ENV_VAR = "KORE_FEATURE_FLAGS_PROFILE_ID"


class FeatureFlagService:
    """Fetch and cache feature flags from AWS AppConfig or a local JSON file.

    The service enforces a 45-second refresh window and prefers the
    ``feature-flags.json`` fixture at the repository root when it exists.
    Otherwise it falls back to AWS AppConfig using identifiers sourced from
    ``KORE_FEATURE_FLAGS_*`` environment variables within the Mumbai region.

    Example:
        >>> from korefi_commons.feature_flags import FeatureFlagService
        >>> flags = FeatureFlagService()
        >>> flags.is_on("some-flag")
        False
    """

    def __init__(self, local_path: Optional[str] = None) -> None:
        """Create a feature flag service.

        Args:
            local_path: Optional filesystem path to a JSON file that mirrors
                the AppConfig payload. Defaults to ``<repo>/feature-flags.json``.
                When the file is present the service loads flags from disk,
                which is ideal for local development and tests. When absent the
                service polls AWS AppConfig in ``ap-south-1`` every 45 seconds.
                The default file path is ignored by Git and should only exist in
                local environments.
        """

        self.ttl: int = DEFAULT_TTL_SECONDS
        self._token: Optional[str] = None
        self._cache: Dict[str, Any] = {}
        self._last_refresh: float = 0.0

        if local_path is not None:
            self._local_path = Path(local_path)
        else:
            self._local_path = DEFAULT_LOCAL_PATH

        self._application_id: Optional[str] = os.getenv(APPLICATION_ENV_VAR)
        self._environment_id: Optional[str] = os.getenv(ENVIRONMENT_ENV_VAR)
        self._profile_id: Optional[str] = os.getenv(PROFILE_ENV_VAR)
        self._client = None

    def _refresh(self) -> None:
        """Refresh the cached feature flags if the 45-second TTL has expired."""

        now = time.monotonic()
        if now - self._last_refresh < self.ttl:
            logger.debug(
                "Feature flags refreshed within %s seconds, skipping refresh", self.ttl
            )
            return

        try:
            if self._local_path.exists():  # local mock
                with self._local_path.open("r", encoding="utf-8") as handle:
                    self._cache = json.load(handle)
            else:  # real AWS
                if self._client is None:
                    self._client = boto3.client(
                        "appconfigdata", region_name=DEFAULT_REGION
                    )

                if not all(
                    [self._application_id, self._environment_id, self._profile_id]
                ):
                    missing_values = [
                        name
                        for name, value in (
                            (APPLICATION_ENV_VAR, self._application_id),
                            (ENVIRONMENT_ENV_VAR, self._environment_id),
                            (PROFILE_ENV_VAR, self._profile_id),
                        )
                        if not value
                    ]
                    logger.error(
                        "Missing AppConfig identifiers: %s", ", ".join(missing_values)
                    )
                    return

                if not self._token:
                    response = self._client.start_configuration_session(
                        ApplicationIdentifier=self._application_id,
                        EnvironmentIdentifier=self._environment_id,
                        ConfigurationProfileIdentifier=self._profile_id,
                    )
                    self._token = response.get("InitialConfigurationToken")

                if not self._token:
                    logger.error("Failed to acquire initial AppConfig token")
                    return

                resp = self._client.get_latest_configuration(
                    ConfigurationToken=self._token
                )
                self._token = resp.get("NextPollConfigurationToken", self._token)
                body = resp.get("Configuration")
                raw = body.read() if hasattr(body, "read") else (body or b"")
                if raw:
                    self._cache = json.loads(raw.decode("utf-8"))
        except (ClientError, BotoCoreError, OSError, json.JSONDecodeError) as exc:
            logger.error("Failed to refresh feature flags: %s", exc)
        finally:
            self._last_refresh = now

    def is_on(self, name: str, default: bool = False) -> bool:
        """Return the status of a feature flag, falling back to ``default`` when missing."""

        self._refresh()
        value = self._cache.get(name, default)
        if isinstance(value, bool):
            return value

        logger.warning(
            "Feature flag %s contains non-boolean value %r; falling back to %s",
            name,
            value,
            default,
        )
        return bool(default)


@contextmanager
def feature_flag_service(local_path: Optional[str] = None):
    """Context manager that yields a :class:`FeatureFlagService`."""

    service = FeatureFlagService(local_path=local_path)
    try:
        yield service
    finally:
        # No explicit cleanup required; hook provided for API symmetry.
        pass
