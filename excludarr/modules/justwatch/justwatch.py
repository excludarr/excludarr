import re
import requests

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from json import JSONDecodeError
from utils.locales import locales as default_locales

from .exceptions import JustWatchTooManyRequests, JustWatchNotFound, JustWatchBadRequest

_GRAPHQL_SEARCH_MOVIE_QUERY = """query GetSearchTitles(
    $searchTitlesFilter: TitleFilter!,
    $country: Country!,
    $language: Language!,
    $first: Int!,
    $formatPoster: ImageFormat,
    $formatOfferIcon: ImageFormat,
    $profile: PosterProfile,
    $backdropProfile: BackdropProfile,
    $filter: OfferFilter!,
) {
    popularTitles(
    country: $country
    filter: $searchTitlesFilter
    first: $first
    sortBy: POPULAR
    sortRandomSeed: 0
    ) {
        edges {
            ...SearchTitleGraphql
            __typename
        }
        __typename
    }
}

fragment SearchTitleGraphql on PopularTitlesEdge {
    node {
        id
        objectId
        objectType
        content(country: $country, language: $language) {
        title
        fullPath
        originalReleaseYear
        originalReleaseDate
        runtime
        shortDescription
        genres {
            shortName
            __typename
        }
        externalIds {
            imdbId
            __typename
        }
        posterUrl(profile: $profile, format: $formatPoster)
        backdrops(profile: $backdropProfile, format: $formatPoster) {
            backdropUrl
            __typename
        }
        __typename
    }
    offers(country: $country, platform: WEB, filter: $filter) {
        monetizationType
        presentationType
        standardWebURL
        retailPrice(language: $language)
        retailPriceValue
        currency
        package {
            id
            packageId
            clearName
            technicalName
            icon(profile: S100, format: $formatOfferIcon)
            __typename
        }
        id
        __typename
        }
        __typename
    }
    __typename
}
"""

_GRAPHQL_LIST_PROVIDERS_QUERY = """
query GetPackages($platform: Platform! = WEB, $country: Country!) {
    packages(country: $country, platform: $platform, includeAddons: false) {
        clearName
    }
}
"""


class JustWatch(object):
    def __init__(self, locale, ssl_verify=True):
        # Setup base variables
        self.base_url = "https://apis.justwatch.com/graphql"
        self.ssl_verify = ssl_verify

        # Setup session
        self.session = requests.Session()
        self.session.verify = ssl_verify

        # Setup retries on failure
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )

        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        # Setup locale by verifying its input
        self.locale = self._get_full_locale(locale)

    def __exit__(self, *args):
        self.session.close()

    def _build_url(self, path):
        return "{}{}".format(self.base_url, path)

    def _filter_api_error(self, data):

        if data.status_code == 400:
            raise JustWatchBadRequest(data.text)
        elif data.status_code == 404:
            raise JustWatchNotFound()
        elif data.status_code == 429:
            raise JustWatchTooManyRequests()

        try:
            result_json = data.json()
        except JSONDecodeError:
            return data.text

        return result_json

    def _http_request(self, json=None, params=None):
        url = self._build_url("/query")
        headers = {"Content-Type": "application/json"}
        data = {"query": json, "variables": params}
        request = requests.Request("POST", url, headers=headers, json=data)

        prepped = self.session.prepare_request(request)
        result = self.session.send(prepped)

        return self._filter_api_error(result)

    def _get_full_locale(self, locale: str):
        default_locale = "en_US"

        if re.match(r"^[A-Z]{2}$", locale.upper()) and locale.upper() in default_locales.keys():
            return f"{default_locales.get(locale.upper())}_{locale.upper()}"
        elif re.match(r"[a-z]{2}_[A-Z]{2}", locale):
            return locale

        return default_locale

    def get_providers(self):
        query = _GRAPHQL_LIST_PROVIDERS_QUERY
        variables = {"locale": self.locale}
        return self._http_request(query, variables)

    def query_title(self, query, content_type, fast=True, result=None, page=1, **kwargs):
        """
        Query JustWatch API to find information about a title

        :query: the title of the show or movie to search for
        :content_type: can either be 'show' or 'movie'. Can also be a list of types.
        """
        result = {} if result is None else result

        if isinstance(content_type, str):
            content_type = content_type.split(",")

        json = {"query": query, "content_types": content_type}
        if kwargs:
            json.update(kwargs)

        page_result = self._http_request(json=json)
        result.update(page_result)

        if not fast and page < result["total_pages"]:
            page += 1
            self.query_title(query, content_type, fast=fast, result=result, page=page)

        return result

    def get_movie(self, jw_id):
        path = f"/titles/movie/{jw_id}/locale/{self.locale}"

        return self._http_request(path)

    def get_show(self, jw_id):
        path = f"/titles/show/{jw_id}/locale/{self.locale}"

        return self._http_request(path)

    def get_season(self, jw_id):
        path = f"/titles/show_season/{jw_id}/locale/{self.locale}"

        return self._http_request(path)
