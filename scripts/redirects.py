from django.utils.http import url_has_allowed_host_and_scheme


def get_safe_redirect_url(next_url: str | None, host: str, is_secure: bool, default: str = "/") -> str:
    """
    Return next_url if it is safe to redirect to (a relative URL, or an absolute URL on this host),
    otherwise the default. Stops a submitted "next" value being used to redirect users to another site.
    """
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={host}, require_https=is_secure):
        return next_url
    return default
