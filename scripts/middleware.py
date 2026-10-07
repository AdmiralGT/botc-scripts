from django.http import HttpResponse

from scripts import constants

UPLOAD_PATH_PREFIXES = ("/script/upload", "/api/scripts/")
BODY_METHODS = ("POST", "PUT", "PATCH")


class UploadSizeLimitMiddleware:
    """
    Reject oversized upload requests using the Content-Length header, before Django reads or spools the body.

    The field validators still run afterwards and give friendly errors for files that are over the individual
    JSON/PDF limits; this only stops requests that are far larger than any valid upload.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in BODY_METHODS and request.path.startswith(UPLOAD_PATH_PREFIXES):
            try:
                content_length = int(request.headers.get("Content-Length", ""))
            except ValueError:
                return HttpResponse("A Content-Length header is required.", status=411, content_type="text/plain")
            if content_length > constants.MAX_UPLOAD_REQUEST_BYTES:
                return HttpResponse("This upload is too large.", status=413, content_type="text/plain")
        return self.get_response(request)
