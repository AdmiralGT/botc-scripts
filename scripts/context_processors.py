from django.conf import settings


def custom_configuration(_request):
    return {"UPLOAD_DISABLED": settings.UPLOAD_DISABLED, "BANNER": settings.BANNER}
