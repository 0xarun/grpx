# grpx

`grpx` is an AI-powered, multi-provider Python CLI for secure file-oriented workflows and threat intelligence lookups.

## Features
- Multi-provider LLM support: **Ollama**, **OpenAI**, **Claude**, **OpenRouter**.
- Unified provider abstraction for easy backend extension.
- Local-first file streaming and filtering for large logs.
- Rule-based detectors (`ipv4`, `email`, `url`).
- Threat-intel integrations: **VirusTotal**, **AbuseIPDB**, **IPinfo**.
- Single user config file: `~/.grpx/config.json`.

## Installation

```bash
pip install grpx
```

After install, use:

```bash
grpx --help
```

## Quick Start

### 1) Configure provider
```bash
grpx setup --provider ollama --model llama3 --ollama-url http://localhost:11434
```

### 2) Analyze a file with a prompt
```bash
grpx -f app.log -p "Summarize failures and likely root causes" --include "error|warn"
```

### 3) Run detector
```bash
grpx --detect ipv4 -f firewall.log
```

### 4) Configure threat-intel keys
```bash
grpx threat-intel setup --virustotal-key VT_KEY --abuseipdb-key ABUSE_KEY --ipinfo-key IPINFO_KEY
```

### 5) Lookup IP intelligence
```bash
grpx threat-intel lookup --ip 8.8.8.8
```

## Command Reference

### Global
- `-f, --file`: Input file path.
- `-p, --prompt`: Prompt text for AI execution.
- `--include`: Include regex for streamed lines.
- `--exclude`: Exclude regex for streamed lines.
- `--detect NAME`: Run built-in detector.

### Subcommands
- `grpx setup`: Configure provider/model/credentials.
- `grpx threat-intel setup`: Store API keys for VT/AbuseIPDB/IPinfo.
- `grpx threat-intel lookup --ip IP`: Query all configured threat-intel sources.

## Configuration

`grpx` stores config at:

```text
~/.grpx/config.json
```

Default shape:

```json
{
  "provider": {
    "name": "ollama",
    "model": "llama3",
    "ollama_url": "http://localhost:11434",
    "openai_api_key": "",
    "claude_api_key": "",
    "openrouter_api_key": "",
    "openrouter_base_url": "https://openrouter.ai/api/v1"
  },
  "threat_intel": {
    "virustotal_api_key": "",
    "abuseipdb_api_key": "",
    "ipinfo_api_key": ""
  },
  "execution": {
    "allow_content_to_ai": false,
    "max_lines": 10000
  }
}
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## Security Model
By default `grpx` does **not** send raw file content to the LLM; it streams files locally, computes metadata summaries, and sends only summaries unless explicitly enabled.

## License
MIT
