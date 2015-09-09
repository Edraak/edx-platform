from django.utils.http import is_safe_url


def get_any_safe_url(hosts, urls):
    """
    Get any safe URL from a list of URLs in any given host.

    :param hosts: A list of hosts to mark as safe.
    :param urls: A list of possible URLs.
    :return: Any safe URL
    """
    for url in urls:
        for host in hosts:
            if is_safe_url(url, host):
                return url

    return None
