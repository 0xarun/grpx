"""Threat intelligence orchestration."""

from __future__ import annotations

from .clients import AbuseIPDBClient, IPinfoClient, VirusTotalClient


class ThreatIntelService:
    def __init__(self, config: dict) -> None:
        self.config = config

    def lookup_ip(self, ip: str, full: bool = False) -> dict:
        keys = self.config["threat_intel"]
        results: dict[str, dict] = {}

        if keys.get("virustotal_api_key"):
            vt = VirusTotalClient(keys["virustotal_api_key"]).lookup_ip(ip)
            results["virustotal"] = vt if full else self._summarize_virustotal(vt)

        if keys.get("abuseipdb_api_key"):
            abuse = AbuseIPDBClient(keys["abuseipdb_api_key"]).lookup_ip(ip)
            results["abuseipdb"] = abuse if full else self._summarize_abuseipdb(abuse)

        if keys.get("ipinfo_api_key"):
            ipinfo = IPinfoClient(keys["ipinfo_api_key"]).lookup_ip(ip)
            results["ipinfo"] = ipinfo if full else self._summarize_ipinfo(ipinfo)

        return results

    @staticmethod
    def _summarize_virustotal(payload: dict) -> dict:
        attrs = payload.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        return {
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
            "reputation": attrs.get("reputation"),
        }

    @staticmethod
    def _summarize_abuseipdb(payload: dict) -> dict:
        data = payload.get("data", {})
        return {
            "abuse_confidence_score": data.get("abuseConfidenceScore"),
            "total_reports": data.get("totalReports"),
            "country_code": data.get("countryCode"),
            "usage_type": data.get("usageType"),
        }

    @staticmethod
    def _summarize_ipinfo(payload: dict) -> dict:
        privacy = payload.get("privacy", {})
        return {
            "ip": payload.get("ip"),
            "bogon": payload.get("bogon", False),
            "hosting": privacy.get("hosting"),
            "vpn": privacy.get("vpn"),
            "proxy": privacy.get("proxy"),
            "tor": privacy.get("tor"),
        }
