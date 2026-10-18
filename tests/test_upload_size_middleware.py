import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from scripts import constants
from scripts.middleware import UploadSizeLimitMiddleware

TOO_LARGE = str(constants.MAX_UPLOAD_REQUEST_BYTES + 1)


@pytest.fixture
def middleware():
    return UploadSizeLimitMiddleware(lambda request: HttpResponse("ok"))


def make_request(method, path, content_length):
    return getattr(RequestFactory(), method)(
        path,
        data=b"x",
        content_type="application/octet-stream",
        CONTENT_LENGTH=content_length,
    )


@pytest.mark.parametrize(
    "method, path",
    [
        ("post", "/script/upload"),
        ("post", "/api/scripts/"),
        ("put", "/api/scripts/5/"),
        ("patch", "/api/scripts/5/"),
    ],
)
def test_oversized_upload_requests_are_rejected(middleware, method, path):
    response = middleware(make_request(method, path, TOO_LARGE))
    assert response.status_code == 413


@pytest.mark.parametrize("path", ["/script/upload", "/api/scripts/"])
def test_upload_requests_within_the_limit_are_allowed(middleware, path):
    response = middleware(make_request("post", path, str(constants.MAX_UPLOAD_REQUEST_BYTES)))
    assert response.status_code == 200


@pytest.mark.parametrize("content_length", ["", "not-a-number"])
def test_upload_requests_without_a_valid_content_length_are_rejected(middleware, content_length):
    response = middleware(make_request("post", "/script/upload", content_length))
    assert response.status_code == 411


def test_other_paths_are_not_limited(middleware):
    response = middleware(make_request("post", "/script/1/vote", TOO_LARGE))
    assert response.status_code == 200


def test_reading_the_upload_page_is_not_limited(middleware):
    request = RequestFactory().get("/script/upload", CONTENT_LENGTH=TOO_LARGE)
    assert middleware(request).status_code == 200
