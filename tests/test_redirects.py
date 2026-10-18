import pytest

from scripts.redirects import get_safe_redirect_url

HOST = "botcscripts.com"


@pytest.mark.parametrize(
    "next_url, is_secure, expected",
    [
        ("/script/1", True, "/script/1"),
        ("/script/1?tab=comments-tab", True, "/script/1?tab=comments-tab"),
        ("https://botcscripts.com/script/1", True, "https://botcscripts.com/script/1"),
        ("http://botcscripts.com/script/1", False, "http://botcscripts.com/script/1"),
    ],
)
def test_safe_targets_are_kept(next_url, is_secure, expected):
    assert get_safe_redirect_url(next_url, HOST, is_secure) == expected


@pytest.mark.parametrize(
    "next_url",
    [
        "https://evil.example/",
        "//evil.example/",
        "///evil.example/",
        "/\\evil.example",
        "javascript:alert(1)",
        "https://botcscripts.com.evil.example/",
    ],
)
def test_unsafe_targets_fall_back_to_the_default(next_url):
    assert get_safe_redirect_url(next_url, HOST, True) == "/"


def test_plain_http_is_rejected_when_the_request_is_secure():
    assert get_safe_redirect_url("http://botcscripts.com/script/1", HOST, True) == "/"


@pytest.mark.parametrize("next_url", [None, ""])
def test_missing_target_falls_back_to_the_default(next_url):
    assert get_safe_redirect_url(next_url, HOST, True) == "/"


def test_custom_default_is_used():
    assert get_safe_redirect_url("https://evil.example/", HOST, True, default="/collections") == "/collections"
