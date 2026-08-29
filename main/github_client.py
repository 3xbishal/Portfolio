"""
Thin GitHub REST API client for the admin GitHub browser.

Read-only: lists repos (public + private) the configured token can see,
browses file trees, views file content, lists commits, and proxies zip
downloads. The token is read from settings.GITHUB_TOKEN (env-only, no DB
storage, no in-app editing UI) and never reaches the browser -- every call
happens server-side.
"""
import requests
from django.conf import settings
from django.core.cache import cache

API_ROOT = 'https://api.github.com'
REQUEST_TIMEOUT = 10
CACHE_TTL = 300  # 5 minutes


class GithubError(Exception):
    """Raised for any GitHub API failure (network, auth, rate limit, 404)."""


def is_configured():
    return bool(getattr(settings, 'GITHUB_TOKEN', ''))


def _headers(accept='application/vnd.github+json'):
    token = getattr(settings, 'GITHUB_TOKEN', '')
    if not token:
        raise GithubError('GITHUB_TOKEN is not configured.')
    return {
        'Authorization': f'token {token}',
        'Accept': accept,
        # GitHub rejects requests with no User-Agent regardless of auth.
        'User-Agent': 'portfolio-admin-github-browser',
        'X-GitHub-Api-Version': '2022-11-28',
    }


def _parse_link_header(response):
    """Return e.g. {'next': url, 'prev': url} parsed from the Link header."""
    links = {}
    header = response.headers.get('Link')
    if not header:
        return links
    for part in header.split(','):
        section = part.split(';')
        if len(section) < 2:
            continue
        url = section[0].strip().strip('<>')
        rel = section[1].strip()
        if rel.startswith('rel="') and rel.endswith('"'):
            links[rel[5:-1]] = url
    return links


def _get(path_or_url, *, accept='application/vnd.github+json', params=None, stream=False):
    url = path_or_url if path_or_url.startswith('http') else f'{API_ROOT}{path_or_url}'
    try:
        response = requests.get(
            url, headers=_headers(accept), params=params,
            timeout=REQUEST_TIMEOUT, stream=stream,
        )
    except requests.RequestException as exc:
        raise GithubError(f'Could not reach GitHub: {exc}') from exc
    if response.status_code == 401:
        raise GithubError('GitHub rejected the token (unauthorized).')
    if response.status_code == 403:
        raise GithubError('GitHub API rate limit reached or access forbidden.')
    if response.status_code == 404:
        raise GithubError('Not found on GitHub.')
    if not response.ok:
        raise GithubError(f'GitHub API error ({response.status_code}).')
    return response


def list_repos(page=1, per_page=30, refresh=False):
    """All repos the token can see (owned, collaborator, org member) -- no
    affiliation filter, so nothing is silently left out."""
    cache_key = f'gh_repos_{page}_{per_page}'
    if not refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    response = _get('/user/repos', params={'sort': 'updated', 'page': page, 'per_page': per_page})
    result = {'repos': response.json(), 'links': _parse_link_header(response)}
    cache.set(cache_key, result, CACHE_TTL)
    return result


def list_branches(owner, repo):
    cache_key = f'gh_branches_{owner}_{repo}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    response = _get(f'/repos/{owner}/{repo}/branches', params={'per_page': 100})
    result = response.json()
    cache.set(cache_key, result, CACHE_TTL)
    return result


def get_contents(owner, repo, path='', ref=None, refresh=False):
    """Returns {'type': 'dir', 'entries': [...]} or {'type': 'file', 'meta': {...}}."""
    cache_key = f'gh_contents_{owner}_{repo}_{path}_{ref}'
    if not refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    params = {'ref': ref} if ref else None
    response = _get(f'/repos/{owner}/{repo}/contents/{path}', params=params)
    data = response.json()
    result = {'type': 'dir', 'entries': data} if isinstance(data, list) else {'type': 'file', 'meta': data}
    cache.set(cache_key, result, CACHE_TTL)
    return result


def get_file_raw(owner, repo, path, ref=None):
    """Raw file bytes, sidestepping the ~1MB base64-JSON size ceiling of the
    default Accept header."""
    params = {'ref': ref} if ref else None
    response = _get(
        f'/repos/{owner}/{repo}/contents/{path}',
        accept='application/vnd.github.raw', params=params,
    )
    return response.content


def list_commits(owner, repo, ref=None, page=1, per_page=30):
    params = {'page': page, 'per_page': per_page}
    if ref:
        params['sha'] = ref
    response = _get(f'/repos/{owner}/{repo}/commits', params=params)
    return {'commits': response.json(), 'links': _parse_link_header(response)}


def stream_zip(owner, repo, ref):
    """
    Proxy a repo zipball download, reattaching auth on the redirect hop.

    GET /repos/{owner}/{repo}/zipball/{ref} redirects (302) to
    codeload.github.com -- a different host. `requests` strips the
    Authorization header on cross-host redirects by default, which would
    otherwise silently break private-repo downloads (404) while public
    repos kept working, a false-confidence trap. So the redirect is
    followed manually with the auth header reattached.
    """
    url = f'{API_ROOT}/repos/{owner}/{repo}/zipball/{ref}'
    try:
        probe = requests.get(url, headers=_headers(), timeout=REQUEST_TIMEOUT, allow_redirects=False)
    except requests.RequestException as exc:
        raise GithubError(f'Could not reach GitHub: {exc}') from exc

    target_url = url
    if probe.status_code in (301, 302, 303, 307, 308):
        location = probe.headers.get('Location')
        if not location:
            raise GithubError('GitHub redirect had no Location header.')
        target_url = location
    elif not probe.ok:
        raise GithubError(f'GitHub API error ({probe.status_code}).')

    try:
        response = requests.get(target_url, headers=_headers(), timeout=REQUEST_TIMEOUT, stream=True)
    except requests.RequestException as exc:
        raise GithubError(f'Could not reach GitHub: {exc}') from exc
    if not response.ok:
        raise GithubError(f'GitHub API error ({response.status_code}).')
    return response
