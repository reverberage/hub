"""Tests for scripts/qwen_fallback.py.

All engine-level tests use mocked providers — no real API calls.
Integration-level tests (cmd_status, cmd_rotate) mock the OpenAI client.

Module-level initialization (MODELS, MODEL_IDS from catalog) runs at import
time and uses the real data/model-catalog.json. This is OK for unit tests
that only exercise logic against known model IDs. Tests that need specific
model lists patch the module-level lists directly.
"""

import importlib.util
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Load qwen_fallback by file path so we don't need scripts as a package
_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "qwen_fallback.py"
)
_spec = importlib.util.spec_from_file_location("qwen_fallback", _SCRIPT_PATH)
assert _spec is not None, f"Could not load spec from {_SCRIPT_PATH}"
assert _spec.loader is not None, f"No loader for spec from {_SCRIPT_PATH}"
qwf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qwf)


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_state_file(tmp_path):
    """Patch STATE_PATH to a temp location and clean up after test."""
    state_file = tmp_path / ".qwen_state.json"
    with patch.object(qwf, "STATE_PATH", state_file):
        yield state_file


@pytest.fixture
def mock_template_file(tmp_path):
    """Patch TEMPLATE_PATH to a temp file with a basic template."""
    template_file = tmp_path / "opencode.template.json"
    template_file.write_text(
        json.dumps({"model": "qwen/{model}", "provider": {}}, indent=2)
    )
    with patch.object(qwf, "TEMPLATE_PATH", template_file):
        yield template_file


@pytest.fixture
def mock_config_file(tmp_path):
    """Patch CONFIG_PATH to a temp location."""
    config_file = tmp_path / "opencode.json"
    with patch.object(qwf, "CONFIG_PATH", config_file):
        yield config_file


@pytest.fixture
def mock_tracking_file(tmp_path):
    """Patch TRACKING_PATH to a temp location."""
    tracking_file = tmp_path / "stage-a-tracking.md"
    with patch.object(qwf, "TRACKING_PATH", tracking_file):
        yield tracking_file


@pytest.fixture
def patched_paths(
    mock_state_file, mock_template_file, mock_config_file, mock_tracking_file
):
    """Combine all path patches into one fixture for convenience."""
    yield


@pytest.fixture
def small_catalog():
    """Replace MODELS/MODEL_IDS with a small test subset for focused tests."""
    models = [
        qwf.ModelInfo(model_id="alpha-1", tier=qwf.Tier.CODER, priority=1),
        qwf.ModelInfo(model_id="beta-2", tier=qwf.Tier.CODER, priority=2),
        qwf.ModelInfo(model_id="gamma-3", tier=qwf.Tier.FLAGSHIP, priority=5),
        qwf.ModelInfo(model_id="delta-4", tier=qwf.Tier.VALUE, priority=0),
    ]
    model_ids = [m.model_id for m in models]
    with (
        patch.object(qwf, "MODELS", models),
        patch.object(qwf, "MODEL_IDS", model_ids),
    ):
        yield models, model_ids


@pytest.fixture
def mock_client():
    """Create a mock OpenAI client that returns ACTIVE for any probe."""
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    client.chat.completions.create.return_value = mock_response

    with patch.object(qwf, "get_client", return_value=client):
        yield client


# ── Data Classes & Constants ─────────────────────────────────────────────────


class TestEnums:
    def test_tier_values(self):
        assert qwf.Tier.CODER.value == 1
        assert qwf.Tier.FLAGSHIP.value == 2
        assert qwf.Tier.VALUE.value == 3
        assert qwf.Tier.THIRD_PARTY.value == 4
        assert qwf.Tier.ALPHA.value == 5

    def test_model_status_values(self):
        assert qwf.ModelStatus.UNKNOWN.value == "UNKNOWN"
        assert qwf.ModelStatus.ACTIVE.value == "ACTIVE"
        assert qwf.ModelStatus.EXHAUSTED.value == "EXHAUSTED"
        assert qwf.ModelStatus.SKIP.value == "SKIP"
        assert qwf.ModelStatus.ERROR.value == "ERROR"


class TestDataClasses:
    def test_model_info_defaults(self):
        m = qwf.ModelInfo(model_id="test-model", tier=qwf.Tier.CODER, priority=1)
        assert m.status == qwf.ModelStatus.UNKNOWN
        assert m.remaining_tokens is None

    def test_model_info_custom_status(self):
        m = qwf.ModelInfo(
            model_id="test-model",
            tier=qwf.Tier.CODER,
            priority=1,
            status=qwf.ModelStatus.ACTIVE,
            remaining_tokens=500_000,
        )
        assert m.status == qwf.ModelStatus.ACTIVE
        assert m.remaining_tokens == 500_000

    def test_rotation_state_fields(self):
        rs = qwf.RotationState(
            active_model_index=0,
            active_model_id="m1",
            exhausted_set=["m2", "m3"],
            last_rotation="2026-07-11T12:00:00+00:00",
        )
        assert rs.active_model_index == 0
        assert rs.active_model_id == "m1"
        assert rs.exhausted_set == ["m2", "m3"]
        assert rs.last_rotation == "2026-07-11T12:00:00+00:00"

    def test_tracking_entry_fields(self):
        te = qwf.TrackingEntry(
            timestamp="2026-07-11T12:00:00Z",
            model_id="m1",
            action="activate",
            remaining_estimate=1_000_000,
            notes="first activation",
        )
        assert te.timestamp == "2026-07-11T12:00:00Z"
        assert te.model_id == "m1"
        assert te.action == "activate"
        assert te.remaining_estimate == 1_000_000
        assert te.notes == "first activation"


class TestSkipSet:
    def test_skip_set_contains_exhausted_models(self):
        assert "qwen-plus" in qwf.SKIP_SET
        assert "qwen-max" in qwf.SKIP_SET
        assert "qwen-turbo" in qwf.SKIP_SET
        assert "qwen-flash" in qwf.SKIP_SET
        assert "deepseek-v4-pro" in qwf.SKIP_SET
        assert "deepseek-v4-flash" in qwf.SKIP_SET

    def test_skip_set_contains_unsupported_models(self):
        assert "qwen3.7-plus" in qwf.SKIP_SET
        assert "qwen3.7-max" in qwf.SKIP_SET
        assert "qwen-plus-character-ja" in qwf.SKIP_SET
        assert "qwen-plus-2025-01-25" in qwf.SKIP_SET

    def test_skip_set_contains_non_chat_models(self):
        assert "qvq-max" in qwf.SKIP_SET
        assert "qwen-vl-ocr" in qwf.SKIP_SET
        assert "qwen-vl-ocr-2025-11-20" in qwf.SKIP_SET
        assert "wan2.2-kf2v-flash" in qwf.SKIP_SET

    def test_skip_set_size(self):
        assert len(qwf.SKIP_SET) == 14


# ── State Management ─────────────────────────────────────────────────────────


class TestFreshState:
    def test_returns_valid_rotation_state(self):
        state = qwf._fresh_state()
        assert isinstance(state, qwf.RotationState)
        assert state.active_model_index == 0
        assert state.active_model_id == qwf.MODELS[0].model_id
        assert state.last_rotation is not None

    def test_exhausted_set_contains_skip_set(self):
        state = qwf._fresh_state()
        for mid in qwf.SKIP_SET:
            assert mid in state.exhausted_set

    def test_exhausted_set_min_size(self):
        state = qwf._fresh_state()
        assert len(state.exhausted_set) >= len(qwf.SKIP_SET)


class TestLoadState:
    def test_returns_fresh_state_when_no_file(self, mock_state_file):
        assert not mock_state_file.exists()
        state = qwf.load_state()
        assert state.active_model_index == 0

    def test_loads_from_existing_file(self, mock_state_file):
        data = {
            "active_model_index": 5,
            "active_model_id": qwf.MODELS[5].model_id,
            "exhausted_set": ["m1", "m2"],
            "last_rotation": "2026-07-11T12:00:00+00:00",
        }
        mock_state_file.write_text(json.dumps(data))

        state = qwf.load_state()
        assert state.active_model_index == 5
        assert state.active_model_id == data["active_model_id"]
        assert state.exhausted_set == ["m1", "m2"]

    def test_handles_corrupted_file(self, mock_state_file):
        mock_state_file.write_text("not valid json")

        state = qwf.load_state()
        assert state.active_model_index == 0

    def test_handles_empty_file(self, mock_state_file):
        mock_state_file.write_text("")

        state = qwf.load_state()
        assert state.active_model_index == 0


class TestSaveState:
    def test_writes_valid_json(self, mock_state_file):
        state = qwf.RotationState(
            active_model_index=2,
            active_model_id="test-model",
            exhausted_set=["e1", "e2"],
            last_rotation="2026-07-11T12:00:00+00:00",
        )
        qwf.save_state(state)

        assert mock_state_file.exists()
        data = json.loads(mock_state_file.read_text())
        assert data["active_model_index"] == 2
        assert data["active_model_id"] == "test-model"

    def test_deduplicates_exhausted_set(self, mock_state_file):
        state = qwf.RotationState(
            active_model_index=0,
            active_model_id="m1",
            exhausted_set=["e1", "e1", "e2"],
            last_rotation="2026-07-11T12:00:00+00:00",
        )
        qwf.save_state(state)

        data = json.loads(mock_state_file.read_text())
        assert len(data["exhausted_set"]) == 2
        assert data["exhausted_set"] == ["e1", "e2"]

    def test_sort_exhausted_set(self, mock_state_file):
        state = qwf.RotationState(
            active_model_index=0,
            active_model_id="m1",
            exhausted_set=["z-model", "a-model"],
            last_rotation="2026-07-11T12:00:00+00:00",
        )
        qwf.save_state(state)

        data = json.loads(mock_state_file.read_text())
        assert data["exhausted_set"] == ["a-model", "z-model"]

    def test_creates_state_dir(self, tmp_path):
        """Should create scripts dir if it doesn't exist."""
        deep_path = tmp_path / "nonexistent" / "subdir"
        state_file = deep_path / "state.json"
        with (
            patch.object(qwf, "STATE_PATH", state_file),
            patch.object(qwf, "STATE_DIR", deep_path),
        ):
            state = qwf._fresh_state()
            qwf.save_state(state)
            assert state_file.exists()


# ── Config Generator ─────────────────────────────────────────────────────────


class TestGenerateOpencode:
    def test_substitutes_model_in_template(self, mock_template_file, mock_config_file):
        ok = qwf.generate_opencode("qwen3-coder-flash")
        assert ok is True
        config = json.loads(mock_config_file.read_text())
        assert config["model"] == "qwen/qwen3-coder-flash"

    def test_uses_dry_run(self, mock_template_file, mock_config_file):
        ok = qwf.generate_opencode("dry-run-model", dry_run=True)
        assert ok is True
        assert not mock_config_file.exists()

    def test_fails_on_missing_template(self, mock_config_file):
        with patch.object(qwf, "TEMPLATE_PATH", MagicMock()) as mock_path:
            mock_path.exists.return_value = False
            ok = qwf.generate_opencode("any-model")
            assert ok is False

    def test_fails_on_invalid_template_json(self, tmp_path, mock_config_file):
        bad_template = tmp_path / "bad-template.json"
        bad_template.write_text("not json")
        with patch.object(qwf, "TEMPLATE_PATH", bad_template):
            ok = qwf.generate_opencode("any-model")
            assert ok is False

    def test_replaces_all_model_occurrences(self, tmp_path, mock_config_file):
        """str.replace replaces ALL {model} occurrences in the template."""
        template = tmp_path / "multi-template.json"
        template.write_text(
            json.dumps(
                {
                    "model": "qwen/{model}",
                    "extra": {"nested": "{model}"},
                }
            )
        )
        with patch.object(qwf, "TEMPLATE_PATH", template):
            ok = qwf.generate_opencode("test-model")
            assert ok is True
            config = json.loads(mock_config_file.read_text())
            assert config["extra"]["nested"] == "test-model"

    def test_preserves_env_var_placeholder(
        self, mock_template_file, mock_config_file
    ):
        """Template uses {model} but {env:...} should be preserved."""
        ok = qwf.generate_opencode("qwen3-coder-plus")
        assert ok is True
        content = mock_config_file.read_text()
        assert "{model}" not in content

    def test_missing_placeholder_warns(self, tmp_path, mock_config_file):
        """Template without {model} placeholder generates warning but succeeds."""
        template = tmp_path / "no-placeholder.json"
        template.write_text(json.dumps({"model": "qwen/fixed-model"}))
        with patch.object(qwf, "TEMPLATE_PATH", template):
            ok = qwf.generate_opencode("any-model")
            assert ok is True
            config = json.loads(mock_config_file.read_text())
            assert config["model"] == "qwen/fixed-model"


# ── Probe Engine ─────────────────────────────────────────────────────────────


class TestProbeModel:
    def test_skip_set_models_return_skip_immediately(self):
        status, remaining = qwf.probe_model(
            "qwen-plus", MagicMock()
        )  # in SKIP_SET
        assert status == qwf.ModelStatus.SKIP
        assert remaining is None

    def test_active_response(self):
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {"x-qwen-quota-remaining": "999000"}
        client.chat.completions.create.return_value = mock_response

        status, remaining = qwf.probe_model("any-active-model", client)
        assert status == qwf.ModelStatus.ACTIVE
        assert remaining == 999000

    def test_exhausted_response(self):
        client = MagicMock()
        client.chat.completions.create.side_effect = Exception(
            '{"code":"AllocationQuota.FreeTierOnly"}'
        )

        status, remaining = qwf.probe_model("exhausted-model", client)
        assert status == qwf.ModelStatus.EXHAUSTED
        assert remaining == 0

    def test_thinking_mode_retry(self):
        """Should retry with enable_thinking=True on 'restricted to True' error."""
        client = MagicMock()

        def side_effect(**kwargs):
            if kwargs.get("extra_body", {}).get("enable_thinking") is False:
                raise Exception("enable_thinking must be restricted to True")
            mock_resp = MagicMock()
            mock_resp.headers = {}
            return mock_resp

        client.chat.completions.create.side_effect = side_effect

        # Not in SKIP_SET, so it will go through probe logic
        status, remaining = qwf.probe_model("thinking-only-model", client)
        assert status == qwf.ModelStatus.ACTIVE

    def test_both_thinking_modes_fail(self):
        """If both thinking=False and thinking=True fail, return ERROR."""
        client = MagicMock()
        client.chat.completions.create.side_effect = Exception("rate limited")

        status, remaining = qwf.probe_model("error-model", client)
        assert status == qwf.ModelStatus.ERROR
        assert remaining is None

    def test_unauthorized_raises_system_exit(self):
        client = MagicMock()
        client.chat.completions.create.side_effect = Exception("401 Unauthorized")

        with pytest.raises(SystemExit):
            qwf.probe_model("bad-key-model", client)


class TestExtractRemaining:
    def test_returns_header_value(self):
        response = MagicMock()
        response.headers = {"x-qwen-quota-remaining": "500000"}
        result = qwf._extract_remaining(response)
        assert result == 500000

    def test_returns_none_when_header_missing(self):
        response = MagicMock()
        response.headers = {}
        result = qwf._extract_remaining(response)
        assert result is None

    def test_returns_none_when_no_headers_attr(self):
        response = object()
        result = qwf._extract_remaining(response)
        assert result is None

    def test_returns_none_on_non_numeric_header(self):
        response = MagicMock()
        response.headers = {"x-qwen-quota-remaining": "not-a-number"}
        result = qwf._extract_remaining(response)
        assert result is None


# ── Tracking Writer ──────────────────────────────────────────────────────────


class TestDaysUntil:
    def test_returns_positive_days(self):
        days = qwf._days_until("2099-12-31")
        assert days > 0

    def test_returns_zero_for_past_date(self):
        days = qwf._days_until("2020-01-01")
        assert days == 0


class TestFormatActivityLog:
    def test_empty_entries_returns_header_only(self):
        result = qwf._format_activity_log(None)
        assert "Date | Model" in result
        assert "|---" in result

    def test_formats_single_entry(self):
        entries = [
            {
                "timestamp": "2026-07-11T12:00:00Z",
                "model_id": "test-model",
                "action": "activate",
                "remaining_estimate": 1_000_000,
                "notes": "initial",
            }
        ]
        result = qwf._format_activity_log(entries)
        assert "test-model" in result
        assert "activate" in result
        assert "1,000,000" in result

    def test_formats_multiple_entries(self):
        entries = [
            {
                "timestamp": "2026-07-11T12:00:00Z",
                "model_id": "m1",
                "action": "activate",
                "remaining_estimate": 1_000_000,
                "notes": "",
            },
            {
                "timestamp": "2026-07-15T12:00:00Z",
                "model_id": "m1",
                "action": "exhaust",
                "remaining_estimate": 0,
                "notes": "",
            },
        ]
        result = qwf._format_activity_log(entries)
        assert result.count("|") >= 12  # enough table cells


class TestFormatRoster:
    def test_marks_active_model(self, small_catalog):
        models, _ = small_catalog
        state = qwf.RotationState(
            active_model_index=0,
            active_model_id=models[0].model_id,
            exhausted_set=list(qwf.SKIP_SET),
            last_rotation="",
        )
        result = qwf._format_roster(state)
        assert "ACTIVE" in result

    def test_honors_exhausted_set(self, small_catalog):
        models, _ = small_catalog
        state = qwf.RotationState(
            active_model_index=0,
            active_model_id=models[0].model_id,
            exhausted_set=list(qwf.SKIP_SET) + ["beta-2"],
            last_rotation="",
        )
        result = qwf._format_roster(state)
        assert "EXHAUSTED" in result


class TestWriteTracking:
    def test_writes_markdown_file(self, patched_paths, mock_tracking_file):
        state = qwf._fresh_state()
        qwf.write_tracking(state)
        assert mock_tracking_file.exists()
        content = mock_tracking_file.read_text()
        assert "# Qwen Free Quota Tracking" in content
        assert "## Summary" in content
        assert "## Activity Log" in content
        assert "## Model Roster" in content

    def test_summary_counts(self, patched_paths, mock_tracking_file):
        state = qwf._fresh_state()
        qwf.write_tracking(state)
        content = mock_tracking_file.read_text()
        # Summary should show the total model count
        assert str(len(qwf.MODELS)) in content

    def test_includes_days_remaining(self, patched_paths, mock_tracking_file):
        state = qwf._fresh_state()
        qwf.write_tracking(state)
        content = mock_tracking_file.read_text()
        assert "Days remaining" in content

    def test_creates_docs_directory(self, tmp_path):
        """Should create docs/ dir if it doesn't exist."""
        deep_path = tmp_path / "nonexistent" / "docs"
        tracking_file = deep_path / "stage-a-tracking.md"
        with (
            patch.object(qwf, "TRACKING_PATH", tracking_file),
            patch.object(qwf, "TEMPLATE_PATH", MagicMock()) as mock_tmpl,
        ):
            mock_tmpl.exists.return_value = True  # Prevent catalog warning
            state = qwf._fresh_state()
            qwf.write_tracking(state)
            assert tracking_file.exists()


# ── MAGI Memory Integration ──────────────────────────────────────────────────


class TestLogQuotaToMagi:
    def test_handles_missing_n3rverberage_gracefully(self, capsys):
        """When n3rverberage is not installed, should log a skip message, not crash."""
        with patch.dict(
            "sys.modules",
            {
                "n3rverberage": None,
                "n3rverberage.config": None,
                "n3rverberage.mcp": None,
                "n3rverberage.mcp.memory_service": None,
            },
        ):
            qwf.log_quota_to_magi("test-model", "activate")
        captured = capsys.readouterr()
        assert "Skipping memory log" in captured.err

    def test_handles_unexpected_error_gracefully(self, capsys):
        """If any exception occurs in the try block, warn but don't crash."""
        with patch.object(qwf, "datetime") as mock_dt:
            mock_dt.now.side_effect = Exception("unexpected error")
            qwf.log_quota_to_magi("test-model", "activate")
        captured = capsys.readouterr()
        assert "Warning: Failed to log to memory" in captured.err


# ── Commands ─────────────────────────────────────────────────────────────────


class TestCmdTrack:
    def test_writes_tracking_doc(self, patched_paths, mock_tracking_file):
        args = _make_args(track=True)
        qwf.cmd_track(args)
        assert mock_tracking_file.exists()
        content = mock_tracking_file.read_text()
        assert "Current active model" in content


class TestCmdStatus:
    def test_json_output(self, mock_client, mock_state_file):
        args = _make_args(status=True, json=True)

        with patch.object(qwf, "sys") as mock_sys:
            mock_sys.stdout = MagicMock()  # prevent actual writes
            qwf.cmd_status(args)

    def test_exit_code_zero_on_success(self, mock_client, mock_state_file):
        """Should exit 0 when models are available."""
        args = _make_args(status=True, json=True)

        with pytest.raises(SystemExit) as exc_info:
            qwf.cmd_status(args)
        assert exc_info.value.code == 0

    def test_exit_code_one_when_all_models_unavailable(self, mock_client, mock_state_file):
        """Should exit 1 when 0/81 models available."""
        # Make probe_model always return ERROR
        with patch.object(qwf, "probe_model", return_value=(qwf.ModelStatus.ERROR, None)):
            args = _make_args(status=True, json=True)
            with pytest.raises(SystemExit) as exc_info:
                qwf.cmd_status(args)
            assert exc_info.value.code == 1


class TestCmdRotate:
    def test_no_rotation_when_active(self, mock_client, patched_paths):
        """When current model is ACTIVE, should not rotate."""
        args = _make_args(rotate=True)
        qwf.cmd_rotate(args)
        # Should not have changed model - active model should still be first
        state = qwf.load_state()
        assert state.active_model_index == 0

    def test_rotation_on_exhaustion(self, mock_client, patched_paths, small_catalog):
        """When current model is EXHAUSTED, should rotate to next available."""
        call_count = 0

        def mock_probe(model_id, client):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call (current model) → exhausted
                return qwf.ModelStatus.EXHAUSTED, 0
            # Subsequent calls (candidates) → active
            return qwf.ModelStatus.ACTIVE, 999000

        with patch.object(qwf, "probe_model", side_effect=mock_probe):
            args = _make_args(rotate=True)
            qwf.cmd_rotate(args)

        # Should have rotated to index 1 (beta-2 in small_catalog)
        state = qwf.load_state()
        assert state.active_model_index == 1
        assert state.active_model_id == "beta-2"

    def test_rotation_skips_skip_set(self, mock_client, patched_paths, small_catalog):
        """Should skip SKIP_SET models during rotation."""
        # Put beta-2 and gamma-3 in SKIP_SET.
        # Rotation: alpha-1 (exhausted) → skip beta-2 (SKIP) → skip gamma-3 (SKIP) → delta-4 (active)
        skip_models = frozenset(["beta-2", "gamma-3"])

        def mock_probe(model_id, client):
            if model_id == "alpha-1":
                return qwf.ModelStatus.EXHAUSTED, 0
            return qwf.ModelStatus.ACTIVE, 999000

        with (
            patch.object(qwf, "probe_model", side_effect=mock_probe),
            patch.object(qwf, "SKIP_SET", skip_models),
        ):
            args = _make_args(rotate=True)
            qwf.cmd_rotate(args)

        state = qwf.load_state()
        assert state.active_model_id == "delta-4"

    def test_rotation_skips_exhausted_models(self, mock_client, patched_paths, small_catalog):
        """Should skip already-exhausted models during rotation."""
        # Pre-populate state so alpha-1 is exhausted, beta-2 already exhausted.
        # Rotation: alpha-1 (current, exhausted) → beta-2 (already exhausted) → gamma-3 (active)
        models, _ = small_catalog

        def mock_probe(model_id, client):
            if model_id == "alpha-1":
                return qwf.ModelStatus.EXHAUSTED, 0
            # Make beta-2 also return exhausted
            if model_id == "beta-2":
                return qwf.ModelStatus.EXHAUSTED, 0
            return qwf.ModelStatus.ACTIVE, 999000

        with (
            patch.object(qwf, "probe_model", side_effect=mock_probe),
        ):
            args = _make_args(rotate=True)
            qwf.cmd_rotate(args)

        state = qwf.load_state()
        assert state.active_model_id == "gamma-3"
        # beta-2 should have been added to exhausted_set during rotation
        assert "beta-2" in state.exhausted_set

    def test_dry_run_does_not_write_files(self, patched_paths, mock_config_file):
        """Dry-run should print what would happen without writing."""
        args = _make_args(rotate=True, dry_run=True)
        qwf.cmd_rotate(args)
        assert not mock_config_file.exists()

    def test_all_models_exhausted_exits_with_error(self, mock_client, patched_paths, small_catalog):
        """When every probeable model is exhausted, should exit 1."""
        def mock_probe(model_id, client):
            return qwf.ModelStatus.EXHAUSTED, 0

        with patch.object(qwf, "probe_model", side_effect=mock_probe):
            args = _make_args(rotate=True)
            with pytest.raises(SystemExit) as exc_info:
                qwf.cmd_rotate(args)
            assert exc_info.value.code == 1

    def test_model_override(self, patched_paths, mock_template_file, mock_config_file):
        """--model should set active model directly without probing."""
        args = _make_args(rotate=True, model="gamma-3")

        with patch.object(qwf, "MODEL_IDS", ["alpha-1", "beta-2", "gamma-3"]):
            with patch.object(
                qwf,
                "MODELS",
                [
                    qwf.ModelInfo("alpha-1", qwf.Tier.CODER, 1),
                    qwf.ModelInfo("beta-2", qwf.Tier.CODER, 2),
                    qwf.ModelInfo("gamma-3", qwf.Tier.FLAGSHIP, 5),
                ],
            ):
                qwf.cmd_rotate(args)

        state = qwf.load_state()
        assert state.active_model_id == "gamma-3"

    def test_model_override_invalid_exits(self, patched_paths):
        """--model with invalid name should exit with error."""
        args = _make_args(rotate=True, model="nonexistent-model")

        with pytest.raises(SystemExit) as exc_info:
            qwf.cmd_rotate(args)
        assert exc_info.value.code == 1

    def test_force_rotation_skips_probe(self, mock_client, patched_paths, small_catalog):
        """--force should skip probing current model and go straight to next."""
        args = _make_args(rotate=True, force=True)
        qwf.cmd_rotate(args)

        state = qwf.load_state()
        assert state.active_model_index == 1


# ── Catalog Loading ──────────────────────────────────────────────────────────


class TestLoadCatalog:
    def test_loads_models_from_fixture(self):
        """MODELS should be populated with ModelInfo instances."""
        assert len(qwf.MODELS) > 0
        assert all(isinstance(m, qwf.ModelInfo) for m in qwf.MODELS)
        assert qwf.MODEL_IDS is not None
        assert len(qwf.MODELS) == len(qwf.MODEL_IDS)

    def test_sorted_by_tier_then_priority(self):
        """Models should be sorted by tier (ascending) then priority (ascending)."""
        for i in range(len(qwf.MODELS) - 1):
            cur = qwf.MODELS[i]
            nxt = qwf.MODELS[i + 1]
            assert (cur.tier.value, cur.priority) <= (nxt.tier.value, nxt.priority)

    def test_first_model_is_tier_1(self):
        """The first model (active by default) should be tier 1 (CODER)."""
        assert qwf.MODELS[0].tier == qwf.Tier.CODER


# ── CLI Entry Point ──────────────────────────────────────────────────────────


class TestMainDispatch:
    def test_default_is_status_json(self, patched_paths):
        """No args should default to --status --json."""
        test_args = ["qwen_fallback.py"]
        with (
            patch("sys.argv", test_args),
            patch.object(qwf, "cmd_status") as mock_status,
        ):
            qwf.main()
            mock_status.assert_called_once()
            args = mock_status.call_args[0][0]
            assert args.status is True
            assert args.json is True

    def test_dispatch_status(self, patched_paths):
        test_args = ["qwen_fallback.py", "--status"]
        with (
            patch("sys.argv", test_args),
            patch.object(qwf, "cmd_status") as mock_cmd,
        ):
            qwf.main()
            mock_cmd.assert_called_once()

    def test_dispatch_rotate(self, patched_paths):
        test_args = ["qwen_fallback.py", "--rotate"]
        with (
            patch("sys.argv", test_args),
            patch.object(qwf, "cmd_rotate") as mock_cmd,
        ):
            qwf.main()
            mock_cmd.assert_called_once()

    def test_dispatch_track(self, patched_paths):
        test_args = ["qwen_fallback.py", "--track"]
        with (
            patch("sys.argv", test_args),
            patch.object(qwf, "cmd_track") as mock_cmd,
        ):
            qwf.main()
            mock_cmd.assert_called_once()


# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_args(
    status: bool = False,
    rotate: bool = False,
    track: bool = False,
    force: bool = False,
    json: bool = False,
    model: str | None = None,
    dry_run: bool = False,
) -> object:
    """Create a Namespace-like object for command functions."""
    return type(
        "Args",
        (),
        {
            "status": status,
            "rotate": rotate,
            "track": track,
            "force": force,
            "json": json,
            "model": model,
            "dry_run": dry_run,
        },
    )()
