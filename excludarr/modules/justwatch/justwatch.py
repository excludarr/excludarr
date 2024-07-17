import requests
from httpx import post

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from json import JSONDecodeError

# from simplejustwatchapi.justwatch import search

from .exceptions import JustWatchTooManyRequests, JustWatchForbidden, JustWatchNotFound, JustWatchBadRequest
from .models import MovieSearchResult,ShowSearchResult, Offer


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
        self.locale = self._get_full_locale(locale)

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        url = self._build_url(path)
        request = requests.Request(method, url, headers=headers, json=json, params=params)

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
            locale = "".join([i["full_locale"] for i in jw_locales if i["iso_3166_2"] == locale])

        # If the locale is empty return the default locale
        if not locale:
            return default_locale

        return locale

    def get_providers(self):
        path = f"/providers/locale/{self.locale}"

        return self._http_get(path)

    def query_title(self, query, content_type, fast=True, results = 10):
        """
        Query JustWatch API to find information about a title

        :query: the title of the show or movie to search for
        :content_type: can either be 'SHOW' or 'MOVIE'. Can also be a list of types.
        """
        if isinstance(content_type, str):
            content_type = content_type.upper().split(",")

        # json = {"query": query, "content_types": content_type}
        # if kwargs:
        #     json.update(kwargs)

        # page_result = self._http_post(path, json=json)

        [lang, country] = self.locale.split("_") 
        result = self._search(query, results, lang, country)

        # I don't think we need paging any longer
        # result.update(page_result)

        # if not fast and page < result["total_pages"]:
        #     page += 1
        #     self.query_title(query, content_type, fast=fast, result=result, page=page)

        return result
    
    def query_jwid_providers(self, jwid:str, providers:list[str] = [], forceFlatrate = False):
        [lang, country] = self.locale.split("_") 
        result = self._get_providers(jwid, country)

        return result

    def _search(
        self, title, results=1, language="en", country="US"
    ) -> list[MovieSearchResult] | list[ShowSearchResult]:
        query = """#graphql
query GetSearchTitles(
    $searchTitlesFilter: TitleFilter!
    $country: Country!
    $language: Language!
    $first: Int!
) {
    popularTitles(
        country: $country
        filter: $searchTitlesFilter
        first: $first
    ) {
        edges {
            node {
                ... on MovieOrShow {
                    id
                    objectId
                    objectType
                    content(country: $country, language: $language) {
                        title
                        originalReleaseYear
                        originalReleaseDate
                        externalIds {
                            imdbId
                            tmdbId
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                ... on Show {
                    totalSeasonCount
                    seasons(sortDirection: ASC) {
                        id
                        objectId
                        objectType
                        totalEpisodeCount
                        content(country: $country, language: $language) {
                            seasonNumber
                            title
                        }
                        __typename
                    }
                    __typename
                }
                __typename
            }
            __typename
        }
        __typename
    }
}
    """
        request = {
            "operationName": "GetSearchTitles",
            "query": query,
            "variables": {
                "first": results,
                "searchTitlesFilter": {"searchQuery": title},
                "language": language,
                "country": country,
            },
        }

        #TODO: implement content filter `SHOW` or `MOVIE`
        #TODO: implement content filter by year

        response = post(self.graphql_url, json=request)


        ret = []
        for node in response.json()["data"]["popularTitles"]["edges"]:
            node = node["node"]

            if node["objectType"] == "SHOW":
                ret.append(ShowSearchResult(node))

            elif node["objectType"] == "MOVIE":
                ret.append(MovieSearchResult(node))

        return ret
    
    def _get_providers(self,
        jwid: str, country="US", providers: list[str] = [], forceFlatrate: bool = False
    ) -> list[Offer]:
        query = """#graphql
query GetTitleOffers(
	$nodeId: ID!,
	$country: Country!
	$platform: Platform! = WEB
    $offerFilter: OfferFilter!
) {
	node(id: $nodeId) {
		...TitleDetails
		__typename
	}
	__typename
}

fragment TitleDetails on Node {
  id
  __typename
  ... on MovieOrSeason {
    offers(country: $country, platform: $platform, filter: $offerFilter) {
      monetizationType
			presentationType
      elementCount
			subtitleLanguages
			audioLanguages
      package {
        id
        packageId
        clearName
        shortName
		technicalName
				
        __typename
      }
      __typename
    }
    __typename
  }
}
"""
        # MONETIZATION_TYPES = ["FLATRATE", "RENT", "BUY", "ADS", "FREE"]
        # PRESENTATION_TYPES = ["SD", "HD", "_4K"]
        filter = {}

        if forceFlatrate:
            filter["monetizationTypes"] = ["FLATRATE"]
        if len(providers) > 0:
            filter["packages"] = providers

        request = {
            "operationName": "GetTitleOffers",
            "query": query,
            "variables": {"nodeId": jwid, "country": country, "offerFilter": filter},
        }

        response = post(self.graphql_url, json=request)

        offers = []
        j = response.json()
        if "offers" in j["data"]["node"]:
            for off in j["data"]["node"]["offers"]:
                offers.append(Offer(off))

        return offers
