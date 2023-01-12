from .. import (
    any_bool,
    any_dict,
    any_int,
    any_int_or_null,
    any_list,
    any_string,
    any_string_or_null,
    recursive_compare,
)


def assert_cookies(request_cookies, expected_cookies):
    assert len(request_cookies) == len(expected_cookies)

    # Simple helper to find a cookie by key and value only.
    def match_cookie(cookie, expected):
        for key in expected:
            if cookie[key] != expected[key]:
                return False

        return True

    for cookie in expected_cookies:
        assert next(c for c in request_cookies if match_cookie(c, cookie)) is not None


def assert_headers(request_headers, expected_headers):
    # The browser sets request headers, only assert that the expected headers
    # are included in the request's headers.
    assert len(request_headers) >= len(expected_headers)
    for header in expected_headers:
        assert next(h for h in request_headers if header == h) is not None


def assert_timing_info(timing_info):
    recursive_compare(
        {
            "requestTime": any_int,
            "redirectStart": any_int,
            "redirectEnd": any_int,
            "fetchStart": any_int,
            "dnsStart": any_int,
            "dnsEnd": any_int,
            "connectStart": any_int,
            "connectEnd": any_int,
            "tlsStart": any_int,
            "tlsEnd": any_int,
            "requestStart": any_int,
            "responseStart": any_int,
            "responseEnd": any_int,
        },
        timing_info,
    )


def assert_request_data(request_data, expected_request):
    recursive_compare(
        {
            "bodySize": any_int_or_null,
            "cookies": any_list,
            "headers": any_list,
            "headersSize": any_int,
            "method": any_string,
            "request": any_string,
            "timings": any_dict,
            "url": any_string,
        },
        request_data,
    )

    assert_timing_info(request_data["timings"])

    if "cookies" in expected_request:
        assert_cookies(request_data["cookies"], expected_request["cookies"])
        # While recursive_compare tolerates missing entries in dict, arrays
        # need to have the exact same number of items, and be in the same order.
        # We don't want to assert all headers and cookies, so we do a custom
        # assert for each and then delete it before using recursive_compare.
        del expected_request["cookies"]

    if "headers" in expected_request:
        assert_headers(request_data["headers"], expected_request["headers"])
        # Remove headers before using recursive_compare, see comment for cookies
        del expected_request["headers"]

    recursive_compare(expected_request, request_data)


def assert_base_parameters(
    event,
    context=None,
    is_redirect=None,
    redirect_count=None,
    expected_request=None,
):
    recursive_compare(
        {
            "context": any_string_or_null,
            "navigation": any_string_or_null,
            "isRedirect": any_bool,
            "redirectCount": any_int,
            "request": any_dict,
            "timestamp": any_int,
        },
        event,
    )

    if context is not None:
        assert event["context"] == context

    if is_redirect is not None:
        assert event["isRedirect"] == is_redirect

    if redirect_count is not None:
        assert event["redirectCount"] == redirect_count

    # Assert request data
    if expected_request is not None:
        assert_request_data(event["request"], expected_request)


def assert_before_request_sent_event(
    event,
    context=None,
    is_redirect=None,
    redirect_count=None,
    expected_request=None,
):
    # Assert initiator
    assert isinstance(event["initiator"], dict)
    assert isinstance(event["initiator"]["type"], str)

    # Assert base parameters
    assert_base_parameters(
        event,
        context=context,
        is_redirect=is_redirect,
        redirect_count=redirect_count,
        expected_request=expected_request,
    )


def assert_response_data(response_data, expected_response):
    recursive_compare(
        {
            "bodySize": any_int_or_null,
            "bytesReceived": any_int,
            "content": {
                "size": any_int_or_null,
            },
            "fromCache": any_bool,
            "headersSize": any_int_or_null,
            "protocol": any_string,
            "status": any_int,
            "statusText": any_string,
            "url": any_string,
        },
        response_data,
    )

    if "headers" in expected_response:
        assert_headers(response_data["headers"], expected_response["headers"])
        # Remove headers before using recursive_compare, see comment for cookies
        # in assert_request_data
        del expected_response["headers"]

    recursive_compare(expected_response, response_data)


def assert_response_event(
    event,
    context=None,
    is_redirect=None,
    redirect_count=None,
    expected_request=None,
    expected_response=None,
):
    # Assert response data
    any_dict(event["response"])
    if expected_response is not None:
        assert_response_data(event["response"], expected_response)

    # Assert base parameters
    assert_base_parameters(
        event,
        context=context,
        is_redirect=is_redirect,
        redirect_count=redirect_count,
        expected_request=expected_request,
    )

# Array of status and status text expected to be available in network events
HTTP_STATUS_AND_STATUS_TEXT = [
    (101, "Switching Protocols"),
    (200, "OK"),
    (201, "Created"),
    (202, "Accepted"),
    (203, "Non-Authoritative Information"),
    (204, "No Content"),
    (205, "Reset Content"),
    (206, "Partial Content"),
    (300, "Multiple Choices"),
    (301, "Moved Permanently"),
    (302, "Found"),
    (303, "See Other"),
    (304, "Not Modified"),
    (305, "Use Proxy"),
    (307, "Temporary Redirect"),
    (400, "Bad Request"),
    (401, "Unauthorized"),
    (402, "Payment Required"),
    (403, "Forbidden"),
    (404, "Not Found"),
    (405, "Method Not Allowed"),
    (406, "Not Acceptable"),
    (407, "Proxy Authentication Required"),
    (408, "Request Timeout"),
    (409, "Conflict"),
    (410, "Gone"),
    (411, "Length Required"),
    (412, "Precondition Failed"),
    (415, "Unsupported Media Type"),
    (417, "Expectation Failed"),
    (500, "Internal Server Error"),
    (501, "Not Implemented"),
    (502, "Bad Gateway"),
    (503, "Service Unavailable"),
    (504, "Gateway Timeout"),
    (505, "HTTP Version Not Supported"),
]
