# grpx Architecture and v1 Scaffold

## Overall Architecture Description
`grpx` uses a modular CLI-first architecture with clear layers: the CLI parses commands and routes them to services, configuration is persisted in `~/.grpx/config.json`, providers are loaded through an abstraction (`BaseProvider`) and selected by a factory, file processing is performed locally through streaming/filtering to avoid raw-content exfiltration by default, and threat-intel lookups are orchestrated through dedicated API clients for VirusTotal, AbuseIPDB, and IPinfo.

---

## A) Full Directory Tree with One-Sentence File Purpose

```text
grpx/
├── docs/
│   └── architecture.md
├── src/
│   └── grpx/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── detectors.py
│       ├── executor.py
│       ├── file_stream.py
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── claude.py
│       │   ├── factory.py
│       │   ├── ollama.py
│       │   ├── openai.py
│       │   └── openrouter.py
│       └── threat_intel/
│           ├── __init__.py
│           ├── clients.py
│           └── service.py
├── tests/
│   ├── test_cli.py
│   ├── test_config.py
│   └── test_providers.py
├── pyproject.toml
└── README.md
```

### File Purposes
- `docs/architecture.md`: High-level architecture and complete implementation specification for the project.
- `src/grpx/__init__.py`: Package metadata and version export.
- `src/grpx/cli.py`: Top-level argument parser and command routing for setup, prompt execution, detectors, and threat-intel workflows.
- `src/grpx/config.py`: Load/save/update configuration state in the canonical `~/.grpx/config.json` file.
- `src/grpx/detectors.py`: Rule-based text detectors (`ipv4`, `email`, `url`) and discovery helpers.
- `src/grpx/executor.py`: Prompt execution workflow that combines local file summary and AI provider invocation.
- `src/grpx/file_stream.py`: Memory-efficient line streaming and regex filtering for large text/log files.
- `src/grpx/providers/__init__.py`: Public exports for provider interfaces and factory.
- `src/grpx/providers/base.py`: Abstract provider contract (`generate`) and provider-specific error type.
- `src/grpx/providers/claude.py`: Anthropic Claude backend implementation.
- `src/grpx/providers/factory.py`: Provider selection and instantiation from config.
- `src/grpx/providers/ollama.py`: Ollama local API backend implementation.
- `src/grpx/providers/openai.py`: OpenAI Chat Completions backend implementation.
- `src/grpx/providers/openrouter.py`: OpenRouter backend implementation with configurable base URL.
- `src/grpx/threat_intel/__init__.py`: Public export for threat-intel service.
- `src/grpx/threat_intel/clients.py`: Low-level HTTP clients for VirusTotal, AbuseIPDB, and IPinfo.
- `src/grpx/threat_intel/service.py`: Aggregation layer that calls enabled threat-intel providers.
- `tests/test_cli.py`: CLI parser and command behavior smoke tests.
- `tests/test_config.py`: Config manager persistence and default merge tests.
- `tests/test_providers.py`: Provider factory selection tests.
- `pyproject.toml`: Build/package metadata, dependencies, and the `grpx` console script entry point.
- `README.md`: PyPI-ready usage guide, installation instructions, and examples.

---

## B) `pyproject.toml` for PyPI
The project is configured to publish as `grpx` with console entry point:

- package name: `grpx`
- install command: `pip install grpx`
- executable command: `grpx`
- script target: `grpx.cli:main`

(See repository `pyproject.toml`.)

---

## C) Full CLI Specification

### Global Pattern
- `grpx [GLOBAL FLAGS] [COMMAND] [SUBCOMMAND FLAGS]`

### Prompt/File Mode
- `grpx -f FILE -p PROMPT [--include REGEX] [--exclude REGEX]`
- Purpose: run AI-assisted analysis on a file with optional local pre-filtering.
- Notes: by default, only local summary metadata is sent to AI unless `execution.allow_content_to_ai` is set true.

### Detector Mode
- `grpx --detect NAME -f FILE`
- Supported `NAME` values in v1: `ipv4`, `email`, `url`.
- Output: matching values and total match count.

### Setup Mode
- `grpx setup [--provider PROVIDER] [--model MODEL] [--ollama-url URL] [--api-key KEY] [--openrouter-base-url URL]`
- Providers: `ollama | openai | claude | openrouter`.
- Interactive prompts are used if required flags are omitted.

### Threat Intel Setup
- `grpx threat-intel setup [--virustotal-key KEY] [--abuseipdb-key KEY] [--ipinfo-key KEY]`
- Stores threat-intel credentials to config.

### Threat Intel Lookup
- `grpx threat-intel lookup --ip IP`
- Queries all enabled threat-intel providers and prints aggregated JSON.

### Example Usage
```bash
grpx setup --provider ollama --model llama3 --ollama-url http://localhost:11434
grpx -f auth.log -p "Summarize suspicious login patterns" --include "(error|failed)"
grpx --detect ipv4 -f firewall.log
grpx threat-intel setup --virustotal-key VT_KEY --abuseipdb-key ABUSE_KEY --ipinfo-key IPINFO_KEY
grpx threat-intel lookup --ip 8.8.8.8
```

---

## D) JSON Schema for `~/.grpx/config.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://grpx.dev/schema/config.json",
  "title": "grpx config",
  "type": "object",
  "required": ["provider", "threat_intel", "execution"],
  "properties": {
    "provider": {
      "type": "object",
      "required": ["name", "model"],
      "properties": {
        "name": {
          "type": "string",
          "enum": ["ollama", "openai", "claude", "openrouter"]
        },
        "model": {"type": "string"},
        "ollama_url": {"type": "string", "format": "uri"},
        "openai_api_key": {"type": "string"},
        "claude_api_key": {"type": "string"},
        "openrouter_api_key": {"type": "string"},
        "openrouter_base_url": {"type": "string", "format": "uri"}
      },
      "additionalProperties": false
    },
    "threat_intel": {
      "type": "object",
      "properties": {
        "virustotal_api_key": {"type": "string"},
        "abuseipdb_api_key": {"type": "string"},
        "ipinfo_api_key": {"type": "string"}
      },
      "additionalProperties": false
    },
    "execution": {
      "type": "object",
      "properties": {
        "allow_content_to_ai": {"type": "boolean", "default": false},
        "max_lines": {"type": "integer", "minimum": 1, "default": 10000}
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

---

## E) Provider Interface Design

### Abstract Interface
```python
class BaseProvider(ABC):
    def __init__(self, model: str) -> None:
        self.model = model

    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...
```

### Implementation Contract
Each provider backend:
1. Accepts provider-specific credentials/endpoints in `__init__`.
2. Implements `generate(prompt: str) -> str`.
3. Builds provider-native request payloads.
4. Raises `ProviderError` on non-200 responses.

### Backends in v1
- `OllamaProvider`: POST `/api/generate` to local Ollama URL.
- `OpenAIProvider`: POST `/v1/chat/completions` with bearer key.
- `ClaudeProvider`: POST `/v1/messages` with Anthropic headers.
- `OpenRouterProvider`: POST `/chat/completions` with configurable base URL.

### Factory Pattern
A dedicated `build_provider(config)` function reads `config["provider"]` and returns the selected backend instance.

---

## F) Example Code for Main Components
Implemented modules in this scaffold:
- CLI: `src/grpx/cli.py`
- Providers: `src/grpx/providers/*.py`
- Config manager: `src/grpx/config.py`
- Executor: `src/grpx/executor.py`
- Threat-intel clients: `src/grpx/threat_intel/clients.py`

These files are complete executable examples and can be used as the v1 baseline.

---

## G) Testing Plan (Unit + Integration)

### Unit Tests
1. Config defaults are written on first load.
2. Config deep-merge preserves unspecified defaults.
3. Provider factory returns correct class for each provider.
4. CLI parse behavior routes detector mode and prompt mode.
5. Detector returns expected matches on known input.

### Integration Tests
1. End-to-end CLI setup writes config file at custom HOME.
2. End-to-end detector command reads file and prints match count.
3. Threat-intel lookup with mocked HTTP endpoints aggregates JSON.
4. Prompt executor with mocked provider validates content privacy behavior.

### Example Test Cases Included
- `tests/test_config.py` validates config initialization.
- `tests/test_providers.py` validates provider creation.
- `tests/test_cli.py` validates basic parser routing/exit behavior.

---

## H) README Content Suitable for PyPI
See `README.md` in this repository for a PyPI homepage-ready document containing:
- project overview
- install instructions (`pip install grpx`)
- setup and command examples
- architecture notes
- config format
- development/test instructions

---

## I) Step-by-Step Plan for v1 Build and PyPI Release
1. Finalize scaffold modules and command UX (done in this baseline).
2. Add robust input validation and richer detector library.
3. Add HTTP retry/backoff and typed API response parsing.
4. Implement provider-side streaming for long outputs.
5. Expand tests with mocked network and golden fixtures.
6. Add GitHub Actions for lint/test/package checks.
7. Generate sdist/wheel via `python -m build`.
8. Test publish to TestPyPI and verify `pip install -i` flow.
9. Tag release (`v0.1.0`) and publish to PyPI using trusted publisher or API token.
10. Announce release and gather user feedback for v1.1 roadmap.
