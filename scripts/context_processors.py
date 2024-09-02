from django.conf import settings # import the settings file

def upload_disabled(_request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'UPLOAD_DISABLED': settings.UPLOAD_DISABLED}