#!/usr/bin/env python

import requests

from json import JSONDecodeError

from pyradarr.exceptions import RadarrException, RadarrInvalidIdSupplied, RadarrInvalidApiKey
from pyradarr.v3.movie import Movie

class Radarr(object):

    def __init__(self, base_url, api_key, api_version='3', ssl_verify=True):
        # Setup base variables
        self._api_version = str(api_version)
        self._base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.api_url = '{}/api/v{}'.format(self._base_url, self._api_version)

        # Setup SSL verification
        self.ssl_verify = ssl_verify

        # Setup session
        self.session = requests.Session()
        self.session.headers.update({'X-Api-Key': self.api_key})

        # Register managers based on api version
        self.movie = Movie(self)

    def __exit__(self, *args):
        self.session.close()

    def _build_url(self, path):
        return '{}{}'.format(self.api_url, path)

    def _filter_api_error(self, data):            
        if data.status_code == 400:
            raise InvalidIdSupplied("Invalid ID supplied")
        elif data.status_code == 401:
            raise RadarrInvalidApiKey("Invalid API key")
        elif data.status_code == 404:
            raise RadarrInvalidApiKey("Movie not found")

        try:
            result_json = data.json()
        except JSONDecodeError:
            return data.text

        return result_json

    def http_request(self, method, path, json=None, params=None):
        url = self._build_url(path)
        request = requests.Request(method, url, json=json, params=params)

        prepped = self.session.prepare_request(request)
        result = self.session.send(prepped)

        return self._filter_api_error(result)

    def http_get(self, path, params=None):
        return self.http_request('get', path, params=params)

    def http_delete(self, path, json=None, params=None):
        return self.http_request('delete', path, json=json, params=params)
