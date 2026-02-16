from grpx.providers.base import format_http_error


class _FakeHTTPError:
    def __init__(self, code: int, body: str) -> None:
        self.code = code
        self._body = body

    def read(self) -> bytes:
        return self._body.encode("utf-8")


def test_format_http_error_extracts_payment_hint() -> None:
    err = _FakeHTTPError(402, '{"error": {"message": "Insufficient credit balance"}}')

    message = format_http_error("OpenRouter", err)  # type: ignore[arg-type]

    assert "Insufficient credit balance" in message
    assert "billing/quota issue" in message


def test_format_http_error_extracts_auth_hint() -> None:
    err = _FakeHTTPError(401, '{"error": {"message": "invalid_api_key"}}')

    message = format_http_error("OpenAI", err)  # type: ignore[arg-type]

    assert "invalid_api_key" in message
    assert "check API key validity and permissions" in message
