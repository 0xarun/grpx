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
