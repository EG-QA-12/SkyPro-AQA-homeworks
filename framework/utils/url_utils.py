"""URL helper utilities.

Currently provides function to ensure the anti-bot query parameter
``allow-session=1`` is present in a URL.  Used in headless/NOTGUI mode.

Junior note:  если в URL уже есть знак ``?``, мы добавляем параметр после
``&``.  Если параметр уже присутствует, мы не дублируем его.
"""
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

PARAM_NAME = "allow-session"
PARAM_VALUE = "1"


def ensure_allow_session_param(url: str) -> str:
    """Return *url* with ``allow-session=1`` query parameter present.

    The order of query parameters is preserved (new param appended).  If the
    parameter already present we keep the original url unchanged.
    """
    parsed = urlparse(url)
    query_params = parse_qsl(parsed.query, keep_blank_values=True)
    if any(k == PARAM_NAME for k, _ in query_params):
        return url  # already present
    query_params.append((PARAM_NAME, PARAM_VALUE))
    new_query = urlencode(query_params)
    return urlunparse(parsed._replace(query=new_query))
