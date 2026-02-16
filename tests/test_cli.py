from argparse import Namespace

from grpx.cli import main


def test_main_help_returns_zero() -> None:
    code = main([])
    assert code == 0


def test_detector_requires_file() -> None:
    try:
        main(["--detect", "ipv4"])
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_threat_intel_lookup_shortcut(monkeypatch) -> None:
    called = {"value": False}

    def _fake_lookup(args: Namespace, config_mgr) -> int:
        called["value"] = True
        assert args.ip == "8.8.8.8"
        assert args.full is True
        return 0

    monkeypatch.setattr("grpx.cli._run_threat_intel_lookup", _fake_lookup)

    code = main(["threat-intel", "--lookup", "8.8.8.8", "--full"])

    assert code == 0
    assert called["value"] is True
