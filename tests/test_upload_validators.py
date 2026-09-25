import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from scripts import constants, upload_validators


def test_small_json_upload_is_accepted():
    upload_validators.validate_json_upload_size(SimpleUploadedFile("script.json", b"[]"))


def test_oversized_json_upload_is_rejected():
    upload = SimpleUploadedFile("script.json", b" " * (constants.MAX_JSON_UPLOAD_BYTES + 1))
    with pytest.raises(ValidationError):
        upload_validators.validate_json_upload_size(upload)


def test_json_upload_at_the_limit_is_accepted():
    upload = SimpleUploadedFile("script.json", b" " * constants.MAX_JSON_UPLOAD_BYTES)
    upload_validators.validate_json_upload_size(upload)


def test_oversized_string_payload_is_rejected():
    with pytest.raises(ValidationError):
        upload_validators.validate_json_upload_size(" " * (constants.MAX_JSON_UPLOAD_BYTES + 1))


def test_oversized_parsed_json_payload_is_rejected():
    payload = [{"id": "x" * 100}] * 20000
    with pytest.raises(ValidationError):
        upload_validators.validate_json_upload_size(payload)


def test_small_parsed_json_payload_is_accepted():
    upload_validators.validate_json_upload_size([{"id": "chef"}, {"id": "empath"}])


def test_oversized_pdf_upload_is_rejected():
    upload = SimpleUploadedFile("script.pdf", b"%PDF-1.7" + b" " * constants.MAX_PDF_UPLOAD_BYTES)
    with pytest.raises(ValidationError):
        upload_validators.validate_pdf_upload_size(upload)


def test_real_pdf_header_is_accepted_and_the_file_is_rewound():
    content = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n"
    upload = SimpleUploadedFile("script.pdf", content)
    upload_validators.validate_pdf_signature(upload)
    assert upload.read() == content


@pytest.mark.parametrize(
    "content",
    [
        b"<html><script>alert(1)</script></html>",
        b"MZ\x90\x00 not a pdf",
        b"",
        b"\n%PDF-1.7 preceded by junk",
    ],
)
def test_files_that_are_not_pdfs_are_rejected(content):
    with pytest.raises(ValidationError):
        upload_validators.validate_pdf_signature(SimpleUploadedFile("script.pdf", content))
