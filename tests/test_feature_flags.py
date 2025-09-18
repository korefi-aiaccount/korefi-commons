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
