"""Threat intelligence orchestration."""

from __future__ import annotations

from .clients import AbuseIPDBClient, IPinfoClient, VirusTotalClient


class ThreatIntelService:
    def __init__(self, config: dict) -> None:
        self.config = config

    def lookup_ip(self, ip: str) -> dict:
        keys = self.config["threat_intel"]
        results: dict[str, dict] = {}

        if keys.get("virustotal_api_key"):
            results["virustotal"] = VirusTotalClient(keys["virustotal_api_key"]).lookup_ip(ip)
        if keys.get("abuseipdb_api_key"):
            results["abuseipdb"] = AbuseIPDBClient(keys["abuseipdb_api_key"]).lookup_ip(ip)
        if keys.get("ipinfo_api_key"):
            results["ipinfo"] = IPinfoClient(keys["ipinfo_api_key"]).lookup_ip(ip)

        return results
