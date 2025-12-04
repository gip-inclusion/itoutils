from urllib.parse import parse_qsl, urlsplit

from django.utils.http import urlencode


def add_url_params(url: str, params: dict[str, str]) -> str:
    """Add GET params to provided URL being aware of existing.

    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL

    >> url = 'http://localhost:8000/login/activate_employer_account?next_url=%2Finvitations
    >> new_params = {'test': 'value' }
    >> add_url_params(url, new_params)
    'http://localhost:8000/login/activate_employer_account?next_url=%2Finvitations&test=value
    """

    # Remove params with None values
    params = {key: params[key] for key in params if params[key] is not None}
    try:
        url_parts = urlsplit(url)
    except ValueError:
        # URL is invalid so it's useless to continue.
        return None
    query = dict(parse_qsl(url_parts.query))
    query.update(params)

    new_url = url_parts._replace(query=urlencode(query)).geturl()

    return new_url
