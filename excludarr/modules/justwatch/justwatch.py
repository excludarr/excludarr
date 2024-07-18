import requests
from httpx import post

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from json import JSONDecodeError

# from simplejustwatchapi.justwatch import search

from .exceptions import (
    JustWatchTooManyRequests,
    JustWatchForbidden,
    JustWatchNotFound,
    JustWatchBadRequest,
)
from .models import MovieOffers, SearchResult, Offer, ShowOffers


class JustWatch(object):
    def __init__(self, locale, ssl_verify=True):
        # Setup base variables
        self.base_url = "https://apis.justwatch.com/content"
        self.graphql_url = "https://apis.justwatch.com/graphql"
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

        # self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        # Setup locale by verifying its input
        self._locale = self._get_full_locale(locale)
        [self._language, self._country] = self._locale.split("_")

    def __exit__(self, *args):
        self.session.close()

    def _build_url(self, path):
        return "{}{}".format(self.base_url, path)

    def _filter_api_error(self, data):

        if data.status_code == 400:
            raise JustWatchBadRequest(data.text)
        if data.status_code == 403:
            raise JustWatchForbidden()
        elif data.status_code == 404:
            raise JustWatchNotFound()
        elif data.status_code == 429:
            raise JustWatchTooManyRequests()

        try:
            result_json = data.json()
        except JSONDecodeError:
            return data.text

        return result_json

    def _http_request(self, method, path, json=None, params=None):
        # JustWatch returns a 403 without a reasonable User-Agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        url = self._build_url(path)
        request = requests.Request(
            method, url, headers=headers, json=json, params=params
        )

        prepped = self.session.prepare_request(request)
        result = self.session.send(prepped)

        return self._filter_api_error(result)

    def _http_get(self, path, params=None):
        return self._http_request("get", path, params=params)

    def _http_post(self, path, json=None):
        return self._http_request("post", path, json=json)

    def _http_put(self, path, params=None, json=None):
        return self._http_request("put", path, params=params, json=json)

    def _http_delete(self, path, json=None, params=None):
        return self._http_request("delete", path, json=json, params=params)

    def _get_full_locale(self, locale):
        default_locale = "en_US"
        path = "/locales/state"

        jw_locales = self._http_get(path)

        valid_locale = any([True for i in jw_locales if i["full_locale"] == locale])

        # Check if the locale is a iso_3166_2 Country Code
        if not valid_locale:
            locale = "".join(
                [i["full_locale"] for i in jw_locales if i["iso_3166_2"] == locale]
            )

        # If the locale is empty return the default locale
        if not locale:
            return default_locale

        return locale

    def get_providers(self):
        path = f"/providers/locale/{self._locale}"

        return self._http_get(path)

    def query_movie_offers(
        self, jwid: str, providers: list[str] = [], forceFlatrate=False
    ) -> MovieOffers:
        result_json = self.__get_providers(jwid, providers, forceFlatrate)

        result = []

        for offer in result_json["data"]["node"]["offers"]:
            result.append(Offer(offer))

        return result

    def query_show_offers(
        self, jwid: str, providers: list[str] = [], forceFlatrate=False
    ) -> ShowOffers:
        result_json = self.__get_providers(jwid, providers, forceFlatrate)

        result = {}

        for season in result_json["data"]["node"]["seasons"]:
            season_n = season["content"]["seasonNumber"]
            result[season_n] = {}
            for episode in season["episodes"]:
                episode_n = episode["content"]["episodeNumber"]
                result[season_n][episode_n] = []
                for offer in episode["offers"]:
                    result[season_n][episode_n].append(Offer(offer))

        return result

    def search_movie(
        self, title: str, results=4, year: int | None = None
    ) -> list[SearchResult]:
        res = self.__search(title, "MOVIE", results, year)

        return res

    def search_show(
        self, title: str, results=4, year: int | None = None
    ) -> list[SearchResult]:
        res = self.__search(title, "SHOW", results, year)

        return res

    def __search(
        self, title, objectType: str, results=1, year: int | None = None
    ) -> list[SearchResult]:

        from .queries import SEARCH_QUERY as query

        filter = {}

        filter["searchQuery"] = title
        filter["objectTypes"] = [objectType]
        if year != None:
            filter["releaseYear"] = {
                "min": year,
                "max": year,
            }

        request = {
            "operationName": "GetSearchTitles",
            "query": query,
            "variables": {
                "first": results,
                "searchTitlesFilter": filter,
                "language": self._language,
                "country": self._country,
            },
        }

        response = post(self.graphql_url, json=request)

        ret = []
        for node in response.json()["data"]["popularTitles"]["edges"]:
            ret.append(SearchResult(node["node"]))

        return ret

    def __get_providers(
        self, jwid: str, providers: list[str] = [], forceFlatrate: bool = False
    ):

        from .queries import OFFER_QUERY as query

        # MONETIZATION_TYPES = ["FLATRATE", "RENT", "BUY", "ADS", "FREE"]
        # PRESENTATION_TYPES = ["SD", "HD", "_4K"]
        filter = {}

        filter["bestOnly"] = True

        if forceFlatrate:
            filter["monetizationTypes"] = ["FLATRATE"]
        if len(providers) > 0:
            filter["packages"] = providers

        request = {
            "operationName": "GetTitleOffers",
            "query": query,
            "variables": {
                "nodeId": jwid,
                "language": self._language,
                "country": self._country,
                "offerFilter": filter,
            },
        }

        response = post(self.graphql_url, json=request)

        offers = []

        return response.json()
