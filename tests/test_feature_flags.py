import io
import json
import logging
from pathlib import Path

import pytest

from korefi_commons.feature_flags import FeatureFlagService


@pytest.fixture()
def local_flags_file(tmp_path: Path) -> Path:
    file_path = tmp_path / "feature-flags.json"
    file_path.write_text(json.dumps({"enabled": True, "missing": False}), encoding="utf-8")
    return file_path


def test_local_json_happy_path(local_flags_file: Path) -> None:
    service = FeatureFlagService(local_path=str(local_flags_file))

    assert service.is_on("enabled") is True
    assert service.is_on("missing") is False


def test_ttl_skips_repeated_reads(monkeypatch: pytest.MonkeyPatch, local_flags_file: Path) -> None:
    service = FeatureFlagService(local_path=str(local_flags_file))

    open_calls = 0
    original_open = Path.open

    def counting_open(self: Path, *args, **kwargs):
        nonlocal open_calls
        if self == Path(local_flags_file):
            open_calls += 1
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr("korefi_commons.feature_flags.Path.open", counting_open)

    assert service.is_on("enabled") is True
    assert service.is_on("enabled") is True
    assert open_calls == 1


def test_missing_flag_returns_default(local_flags_file: Path) -> None:
    service = FeatureFlagService(local_path=str(local_flags_file))

    assert service.is_on("does-not-exist", default=True) is True


def test_non_boolean_value_logs_warning(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    file_path = tmp_path / "feature-flags.json"
    file_path.write_text(json.dumps({"weird": "yes"}), encoding="utf-8")
    service = FeatureFlagService(local_path=str(file_path))

    with caplog.at_level(logging.WARNING):
        result = service.is_on("weird")

    assert result is False
    assert any("non-boolean" in message for message in caplog.messages)


def test_appconfig_fetch_when_local_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = {"remote": True}
    local_path = tmp_path / "feature-flags.json"  # intentionally absent

    class FakeAppConfigClient:
        def __init__(self) -> None:
            self.start_calls = 0
            self.get_calls = 0

        def start_configuration_session(self, **kwargs):
            self.start_calls += 1
            return {"InitialConfigurationToken": "token"}

        def get_latest_configuration(self, ConfigurationToken: str):
            assert ConfigurationToken == "token"
            self.get_calls += 1
            return {
                "NextPollConfigurationToken": "next-token",
                "Configuration": io.BytesIO(json.dumps(payload).encode("utf-8")),
            }

    fake_client = FakeAppConfigClient()

    monkeypatch.setenv("KORE_FEATURE_FLAGS_APPLICATION_ID", "app")
    monkeypatch.setenv("KORE_FEATURE_FLAGS_ENVIRONMENT_ID", "env")
    monkeypatch.setenv("KORE_FEATURE_FLAGS_PROFILE_ID", "profile")
    def fake_boto3_client(service_name: str, region_name: str) -> FakeAppConfigClient:
        assert service_name == "appconfigdata"
        assert region_name == "ap-south-1"
        return fake_client

    monkeypatch.setattr(
        "korefi_commons.feature_flags.boto3.client",
        fake_boto3_client,
    )

    service = FeatureFlagService(local_path=str(local_path))

    assert service.is_on("remote") is True
    assert fake_client.start_calls == 1
    assert fake_client.get_calls == 1


def test_ttl_refresh_after_expiry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    file_path = tmp_path / "feature-flags.json"
    file_path.write_text(json.dumps({"switch": True}), encoding="utf-8")

    service = FeatureFlagService(local_path=str(file_path))

    # Start the monotonic clock at a high value so the first read happens.
    time_values = iter([100.0, 144.0, 146.0])
    monkeypatch.setattr(
        "korefi_commons.feature_flags.time.monotonic",
        lambda: next(time_values),
    )

    assert service.is_on("switch") is True

    file_path.write_text(json.dumps({"switch": False}), encoding="utf-8")

    assert service.is_on("switch") is True
    assert service.is_on("switch") is False
