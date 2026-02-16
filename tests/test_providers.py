from grpx.providers.factory import build_provider


def test_build_ollama_provider() -> None:
    config = {
        "provider": {
            "name": "ollama",
            "model": "llama3",
            "ollama_url": "http://localhost:11434",
            "openai_api_key": "",
            "claude_api_key": "",
            "openrouter_api_key": "",
            "openrouter_base_url": "https://openrouter.ai/api/v1",
        }
    }

    provider = build_provider(config)

    assert provider.__class__.__name__ == "OllamaProvider"


def test_build_unsupported_provider_raises() -> None:
    config = {"provider": {"name": "unknown", "model": "x"}}

    try:
        build_provider(config)
        raised = False
    except ValueError:
        raised = True

    assert raised
