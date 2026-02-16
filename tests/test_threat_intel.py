from grpx.threat_intel.service import ThreatIntelService


def _config() -> dict:
    return {
        "threat_intel": {
            "virustotal_api_key": "vt",
            "abuseipdb_api_key": "abuse",
            "ipinfo_api_key": "ipinfo",
        }
    }


def test_lookup_ip_summarized(monkeypatch) -> None:
    monkeypatch.setattr(
        "grpx.threat_intel.service.VirusTotalClient.lookup_ip",
        lambda self, ip: {
            "data": {"attributes": {"last_analysis_stats": {"malicious": 7, "suspicious": 2, "harmless": 1, "undetected": 99}, "reputation": -12}}
        },
    )
    monkeypatch.setattr(
        "grpx.threat_intel.service.AbuseIPDBClient.lookup_ip",
        lambda self, ip: {"data": {"abuseConfidenceScore": 65, "totalReports": 88, "countryCode": "US", "usageType": "Data Center/Web Hosting/Transit"}},
    )
    monkeypatch.setattr(
        "grpx.threat_intel.service.IPinfoClient.lookup_ip",
        lambda self, ip: {"ip": ip, "bogon": False, "privacy": {"vpn": True, "proxy": False, "tor": False, "hosting": True}},
    )

    service = ThreatIntelService(_config())
    out = service.lookup_ip("8.8.8.8")

    assert out["virustotal"]["malicious"] == 7
    assert out["abuseipdb"]["abuse_confidence_score"] == 65
    assert out["ipinfo"]["vpn"] is True
    assert "data" not in out["virustotal"]


def test_lookup_ip_full(monkeypatch) -> None:
    monkeypatch.setattr("grpx.threat_intel.service.VirusTotalClient.lookup_ip", lambda self, ip: {"full": "vt"})
    monkeypatch.setattr("grpx.threat_intel.service.AbuseIPDBClient.lookup_ip", lambda self, ip: {"full": "abuse"})
    monkeypatch.setattr("grpx.threat_intel.service.IPinfoClient.lookup_ip", lambda self, ip: {"full": "ipinfo"})

    service = ThreatIntelService(_config())
    out = service.lookup_ip("1.1.1.1", full=True)

    assert out["virustotal"] == {"full": "vt"}
    assert out["abuseipdb"] == {"full": "abuse"}
    assert out["ipinfo"] == {"full": "ipinfo"}
