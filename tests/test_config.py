from pathlib import Path

from grpx.config import ConfigManager


def test_config_creates_default(tmp_path: Path) -> None:
    cfg_file = tmp_path / "config.json"
    manager = ConfigManager(cfg_file)

    data = manager.load()

    assert cfg_file.exists()
    assert data["provider"]["name"] == "ollama"


def test_update_persists_value(tmp_path: Path) -> None:
    cfg_file = tmp_path / "config.json"
    manager = ConfigManager(cfg_file)

    manager.update(["provider", "name"], "openai")
    data = manager.load()

    assert data["provider"]["name"] == "openai"
