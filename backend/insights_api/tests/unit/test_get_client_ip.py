from src.middleware.get_client_ip import get_client_ip
from fastapi import Request
from unittest.mock import Mock


def test_cloudflare_header_takes_precedence() -> None:
    """CF-Connecting-IP header should be used first when present"""
    request = Mock(spec=Request)
    request.headers = {
        "CF-Connecting-IP": "1.2.3.4",
        "X-Forwarded-For": "5.6.7.8",
        "X-Real-IP": "9.10.11.12",
    }
    request.client = Mock(host="13.14.15.16")

    assert get_client_ip(request) == "1.2.3.4"


def test_x_forwarded_for_fallback() -> None:
    """X-Forwarded-For header should be used when CF header is absent"""
    request = Mock(spec=Request)
    request.headers = {"X-Forwarded-For": "5.6.7.8", "X-Real-IP": "9.10.11.12"}
    request.client = Mock(host="13.14.15.16")

    assert get_client_ip(request) == "5.6.7.8"


def test_x_forwarded_for_with_multiple_ips() -> None:
    """X-Forwarded-For with multiple IPs should return the first one"""
    request = Mock(spec=Request)
    request.headers = {"X-Forwarded-For": "5.6.7.8, 9.10.11.12, 13.14.15.16"}
    request.client = Mock(host="17.18.19.20")

    assert get_client_ip(request) == "5.6.7.8"


def test_x_forwarded_for_with_spaces() -> None:
    """X-Forwarded-For with spaces should be trimmed"""
    request = Mock(spec=Request)
    request.headers = {"X-Forwarded-For": "  5.6.7.8  , 9.10.11.12"}
    request.client = Mock(host="13.14.15.16")

    assert get_client_ip(request) == "5.6.7.8"


def test_x_real_ip_fallback() -> None:
    """X-Real-IP header should be used when CF and X-Forwarded-For are absent"""
    request = Mock(spec=Request)
    request.headers = {"X-Real-IP": "9.10.11.12"}
    request.client = Mock(host="13.14.15.16")

    assert get_client_ip(request) == "9.10.11.12"


def test_request_client_fallback() -> None:
    """request.client.host should be used when all headers are absent"""
    request = Mock(spec=Request)
    request.headers = {}  # type: ignore
    request.client = Mock(host="13.14.15.16")

    assert get_client_ip(request) == "13.14.15.16"


def test_returns_unknown_when_no_ip_available() -> None:
    """Should return 'unknown' when no IP information is available"""
    request = Mock(spec=Request)
    request.headers = {}  # type: ignore
    request.client = None

    assert get_client_ip(request) == "unknown"


def test_empty_cloudflare_header_falls_through() -> None:
    """Empty CF-Connecting-IP should fall through to next header"""
    request = Mock(spec=Request)
    request.headers = {"CF-Connecting-IP": "", "X-Forwarded-For": "5.6.7.8"}
    request.client = Mock(host="13.14.15.16")

    assert get_client_ip(request) == "5.6.7.8"


def test_empty_x_forwarded_for_falls_through() -> None:
    """Empty X-Forwarded-For should fall through to next header"""
    request = Mock(spec=Request)
    request.headers = {"X-Forwarded-For": "", "X-Real-IP": "9.10.11.12"}
    request.client = Mock(host="13.14.15.16")

    assert get_client_ip(request) == "9.10.11.12"


def test_empty_x_real_ip_falls_through() -> None:
    """Empty X-Real-IP should fall through to request.client"""
    request = Mock(spec=Request)
    request.headers = {"X-Real-IP": ""}
    request.client = Mock(host="13.14.15.16")

    assert get_client_ip(request) == "13.14.15.16"
