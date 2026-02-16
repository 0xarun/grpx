"""Command line interface for grpx."""

from __future__ import annotations

import argparse
import json
from getpass import getpass

from grpx.config import ConfigManager
from grpx.detectors import available_detectors, run_detector
from grpx.executor import PromptExecutor
from grpx.providers import ProviderError
from grpx.providers.factory import build_provider
from grpx.threat_intel import ThreatIntelService


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="grpx", description="AI-powered multi-provider CLI platform")
    parser.add_argument("-f", "--file", help="File path for prompt processing")
    parser.add_argument("-p", "--prompt", help="Natural language prompt")
    parser.add_argument("--include", help="Optional include regex for streamed lines")
    parser.add_argument("--exclude", help="Optional exclude regex for streamed lines")
    parser.add_argument("--detect", metavar="NAME", help="Run rule-based detector by name")

    subparsers = parser.add_subparsers(dest="command")

    setup_cmd = subparsers.add_parser("setup", help="Configure AI provider and credentials")
    setup_cmd.add_argument("--provider", choices=["ollama", "openai", "claude", "openrouter"])
    setup_cmd.add_argument("--model")
    setup_cmd.add_argument("--ollama-url")
    setup_cmd.add_argument("--api-key")
    setup_cmd.add_argument("--openrouter-base-url")

    ti_cmd = subparsers.add_parser("threat-intel", help="Threat intelligence operations")
    ti_cmd.add_argument("--lookup", metavar="IP", help="Lookup IP directly without subcommand")
    ti_cmd.add_argument("--full", action="store_true", help="Show full provider responses")
    ti_sub = ti_cmd.add_subparsers(dest="ti_command")

    ti_setup = ti_sub.add_parser("setup", help="Store threat-intel API keys")
    ti_setup.add_argument("--virustotal-key")
    ti_setup.add_argument("--abuseipdb-key")
    ti_setup.add_argument("--ipinfo-key")

    ti_lookup = ti_sub.add_parser("lookup", help="Lookup IP address across providers")
    ti_lookup.add_argument("--ip", required=True)
    ti_lookup.add_argument("--full", action="store_true", help="Show full provider responses")

    return parser


def _run_setup(args: argparse.Namespace, config_mgr: ConfigManager) -> int:
    config = config_mgr.load()
    provider = args.provider or input("Provider (ollama/openai/claude/openrouter): ").strip().lower()
    model = args.model or input("Model name: ").strip()
    config["provider"]["name"] = provider
    config["provider"]["model"] = model

    if provider == "ollama":
        config["provider"]["ollama_url"] = args.ollama_url or input("Ollama URL [http://localhost:11434]: ").strip() or "http://localhost:11434"
    elif provider == "openai":
        config["provider"]["openai_api_key"] = args.api_key or getpass("OpenAI API key: ")
    elif provider == "claude":
        config["provider"]["claude_api_key"] = args.api_key or getpass("Claude API key: ")
    elif provider == "openrouter":
        config["provider"]["openrouter_api_key"] = args.api_key or getpass("OpenRouter API key: ")
        config["provider"]["openrouter_base_url"] = (
            args.openrouter_base_url
            or input("OpenRouter base URL [https://openrouter.ai/api/v1]: ").strip()
            or "https://openrouter.ai/api/v1"
        )
    else:
        raise ValueError("Unsupported provider")

    config_mgr.save(config)
    print("Configuration saved to ~/.grpx/config.json")
    return 0


def _run_threat_intel_setup(args: argparse.Namespace, config_mgr: ConfigManager) -> int:
    config = config_mgr.load()
    section = config["threat_intel"]
    section["virustotal_api_key"] = args.virustotal_key or getpass("VirusTotal API key (optional): ")
    section["abuseipdb_api_key"] = args.abuseipdb_key or getpass("AbuseIPDB API key (optional): ")
    section["ipinfo_api_key"] = args.ipinfo_key or getpass("IPinfo API key (optional): ")
    config_mgr.save(config)
    print("Threat intel keys saved.")
    return 0


def _run_threat_intel_lookup(args: argparse.Namespace, config_mgr: ConfigManager) -> int:
    config = config_mgr.load()
    service = ThreatIntelService(config)
    try:
        results = service.lookup_ip(args.ip, full=args.full)
    except Exception as exc:  # pragma: no cover - network/provider dependent
        print(f"Threat intel lookup failed: {exc}")
        return 1

    if not results:
        print("No threat intel providers are configured. Run: grpx threat-intel setup")
        return 1

    print(json.dumps(results, indent=2))
    return 0


def _run_detector(args: argparse.Namespace) -> int:
    if not args.file:
        raise ValueError("--detect requires --file")
    matches = run_detector(args.detect, file_path=args.file)
    print("\n".join(matches))
    print(f"Matches: {len(matches)}")
    return 0


def _run_prompt(args: argparse.Namespace, config_mgr: ConfigManager) -> int:
    config = config_mgr.load()
    provider = build_provider(config)
    executor = PromptExecutor(provider, allow_content_to_ai=config["execution"]["allow_content_to_ai"])
    try:
        result = executor.apply_to_file(
            file_path=args.file,
            prompt=args.prompt,
            include=args.include,
            exclude=args.exclude,
            max_lines=config["execution"]["max_lines"],
        )
    except ProviderError as exc:
        print(f"LLM request failed: {exc}")
        return 1

    print(result)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    config_mgr = ConfigManager()

    if args.command == "setup":
        return _run_setup(args, config_mgr)

    if args.command == "threat-intel":
        if args.lookup:
            args.ip = args.lookup
            return _run_threat_intel_lookup(args, config_mgr)
        if args.ti_command == "setup":
            return _run_threat_intel_setup(args, config_mgr)
        if args.ti_command == "lookup":
            return _run_threat_intel_lookup(args, config_mgr)
        parser.error("threat-intel requires a subcommand: setup or lookup (or use --lookup)")

    if args.detect:
        return _run_detector(args)

    if args.file and args.prompt:
        return _run_prompt(args, config_mgr)

    parser.print_help()
    print("\nAvailable detectors:", ", ".join(available_detectors()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
