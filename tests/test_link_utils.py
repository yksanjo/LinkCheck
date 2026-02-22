from checker import DeadLinkChecker


def test_normalize_url_removes_fragment_and_trailing_slash():
    checker = DeadLinkChecker("https://example.com")
    assert checker.normalize_url("https://example.com/path/#section") == "https://example.com/path"


def test_is_valid_url_rejects_mailto_and_anchor():
    checker = DeadLinkChecker("https://example.com")
    assert checker.is_valid_url("mailto:hello@example.com") is False
    assert checker.is_valid_url("#local") is False
    assert checker.is_valid_url("https://example.com/page") is True
