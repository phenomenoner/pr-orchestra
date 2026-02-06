"""Unit tests for supervisor.py — risk_level, load_config, matches_any."""

import sys, os
from pathlib import Path

# Make supervisor importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from supervisor import risk_level, load_config, matches_any, Config  # noqa: E402


# ---------------------------------------------------------------------------
# matches_any
# ---------------------------------------------------------------------------
def test_matches_any_basic():
    assert matches_any(".github/workflows/ci.yml", [".github/workflows/**"]) is True
    assert matches_any("src/index.ts", [".github/workflows/**"]) is False

def test_matches_any_auth():
    assert matches_any("src/auth/login.ts", ["**/auth/**"]) is True
    assert matches_any("src/utils/auth_helper.ts", ["**/auth/**"]) is False  # not inside auth/

def test_matches_any_lockfiles():
    assert matches_any("package-lock.json", ["**/*lock*"]) is True
    assert matches_any("yarn.lock", ["**/*lock*"]) is True
    assert matches_any("src/clock.ts", ["**/*lock*"]) is True  # fnmatch quirk — *lock* matches

def test_matches_any_dockerfile():
    assert matches_any("Dockerfile", ["Dockerfile"]) is True
    assert matches_any("docker-compose.yml", ["docker-compose.*"]) is True
    # fnmatch * matches dots too → all docker-compose variants are caught (desired)
    assert matches_any("docker-compose.override.yml", ["docker-compose.*"]) is True


# ---------------------------------------------------------------------------
# risk_level — L0 (docs only)
# ---------------------------------------------------------------------------
def _cfg() -> Config:
    """Default config for tests."""
    return Config(
        block_labels=["do-not-merge", "WIP", "blocked", "needs-human"],
        protected_paths=[
            ".github/workflows/**",
            "**/auth/**",
            "**/security/**",
            "Dockerfile",
            "docker-compose.*",
            "**/*lock*",
        ],
        auto_merge_levels=["L0", "L1"],
        max_files_changed=20,
        max_additions=500,
        max_deletions=500,
    )

def test_docs_only_is_L0():
    files = [
        {"filename": "README.md", "additions": 10, "deletions": 2},
        {"filename": "docs/guide.md", "additions": 5, "deletions": 0},
    ]
    level, reasons = risk_level(files, [], _cfg(), 15, 2)
    assert level == "L0"
    assert "docs-only" in reasons[0]


# ---------------------------------------------------------------------------
# risk_level — L1 (small, safe)
# ---------------------------------------------------------------------------
def test_small_src_change_is_L1():
    files = [
        {"filename": "src/utils.ts", "additions": 20, "deletions": 5},
    ]
    level, reasons = risk_level(files, [], _cfg(), 20, 5)
    assert level == "L1"
    assert "small change" in reasons[0]


# ---------------------------------------------------------------------------
# risk_level — L2 (protected path or size)
# ---------------------------------------------------------------------------
def test_protected_path_is_L2():
    files = [
        {"filename": ".github/workflows/ci.yml", "additions": 30, "deletions": 0},
        {"filename": "src/app.ts", "additions": 10, "deletions": 3},
    ]
    level, reasons = risk_level(files, [], _cfg(), 40, 3)
    assert level == "L2"
    assert any("protected" in r for r in reasons)

def test_too_many_files_is_L2():
    files = [{"filename": f"src/file{i}.ts", "additions": 1, "deletions": 0} for i in range(25)]
    level, reasons = risk_level(files, [], _cfg(), 25, 0)
    assert level == "L2"
    assert any("too many files" in r for r in reasons)

def test_too_many_additions_is_L2():
    files = [{"filename": "src/big.ts", "additions": 600, "deletions": 0}]
    level, reasons = risk_level(files, [], _cfg(), 600, 0)
    assert level == "L2"
    assert any("too many additions" in r for r in reasons)

def test_too_many_deletions_is_L2():
    files = [{"filename": "src/big.ts", "additions": 0, "deletions": 600}]
    level, reasons = risk_level(files, [], _cfg(), 0, 600)
    assert level == "L2"
    assert any("too many deletions" in r for r in reasons)


# ---------------------------------------------------------------------------
# risk_level — L3 (block labels)
# ---------------------------------------------------------------------------
def test_block_label_WIP_is_L3():
    files = [{"filename": "src/x.ts", "additions": 1, "deletions": 0}]
    level, reasons = risk_level(files, ["WIP"], _cfg(), 1, 0)
    assert level == "L3"
    assert "blocked by label" in reasons[0]

def test_block_label_do_not_merge_is_L3():
    files = [{"filename": "src/x.ts", "additions": 1, "deletions": 0}]
    level, reasons = risk_level(files, ["do-not-merge"], _cfg(), 1, 0)
    assert level == "L3"

def test_block_label_overrides_docs_only():
    """Even if all files are docs, a block label forces L3."""
    files = [{"filename": "README.md", "additions": 1, "deletions": 0}]
    level, _ = risk_level(files, ["needs-human"], _cfg(), 1, 0)
    assert level == "L3"


# ---------------------------------------------------------------------------
# load_config — YAML parsing
# ---------------------------------------------------------------------------
def test_load_config_defaults(tmp_path):
    """No config file → defaults."""
    cfg = load_config(tmp_path / "nonexistent.yml")
    assert cfg.merge_mode == "auto_merge"
    assert "L0" in cfg.auto_merge_levels

def test_load_config_parses_inline_comment(tmp_path):
    """Inline YAML comments must be stripped."""
    yml = tmp_path / "cfg.yml"
    yml.write_text(
        'merge_mode: recommend_only  # override\n'
        'max_files_changed: 10\n'
    )
    cfg = load_config(yml)
    assert cfg.merge_mode == "recommend_only"
    assert cfg.max_files_changed == 10

def test_load_config_parses_block_list(tmp_path):
    yml = tmp_path / "cfg.yml"
    yml.write_text(
        'protected_paths:\n'
        '  - "src/secret/**"\n'
        '  - "keys/**"\n'
    )
    cfg = load_config(yml)
    assert "src/secret/**" in cfg.protected_paths
    assert "keys/**" in cfg.protected_paths

def test_load_config_parses_inline_list(tmp_path):
    yml = tmp_path / "cfg.yml"
    yml.write_text('auto_merge_levels: ["L0"]\n')
    cfg = load_config(yml)
    assert cfg.auto_merge_levels == ["L0"]


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
