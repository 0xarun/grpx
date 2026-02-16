"""Threat intelligence API clients."""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlencode
import urllib.request


@dataclass
class VirusTotalClient:
    api_key: str

    def lookup_ip(self, ip: str) -> dict:
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
        request = urllib.request.Request(url, headers={"x-apikey": self.api_key})
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))


@dataclass
class AbuseIPDBClient:
    api_key: str

    def lookup_ip(self, ip: str) -> dict:
        query = urlencode({"ipAddress": ip})
        url = f"https://api.abuseipdb.com/api/v2/check?{query}"
        headers = {"Key": self.api_key, "Accept": "application/json"}
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))


@dataclass
class IPinfoClient:
    api_key: str

    def lookup_ip(self, ip: str) -> dict:
        query = urlencode({"token": self.api_key})
        url = f"https://ipinfo.io/{ip}/json?{query}"
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
