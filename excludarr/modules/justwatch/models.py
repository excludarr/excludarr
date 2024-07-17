class SearchResult:
    id: str
    objectType: str
    title: str
    year: int
    imdbId: str | None
    tmdbId: int | None

    def __init__(self, json):
        self.__from_json(json)

    def __from_json(self, node):
        self.id = node["id"]
        self.ty = node["objectType"]
        self.title = node["content"]["title"]
        self.year = node["content"]["originalReleaseYear"]
        self.imdbId = node["content"]["externalIds"]["imdbId"]
        tmdbId = node["content"]["externalIds"]["tmdbId"]
        self.tmdbId = int(tmdbId) if tmdbId != None else None


class MovieSearchResult(SearchResult):
    def __init__(self, json):
        super().__init__(json)


class Season:
    id: str
    number: int
    title: str

    def __init__(self, id, number, title):
        self.id = id
        self.number = number
        self.title = title


class ShowSearchResult(SearchResult):
    seasons: list[Season]

    def __init__(self, json):
        self.seasons: list[Season] = []

        super().__init__(json)

        if "seasons" in json:
            for s in json["seasons"]:
                self.seasons.append(
                    Season(s["id"], s["content"]["seasonNumber"], s["content"]["title"])
                )


class Offer:
    id: str
    monetizationType: str
    presentationType: str
    providerClearName: str
    providertechnicalName: str
    providerShortName: str
    subtitleLanguages: list[str]
    audioLanguages: list[str]

    def __init__(self, json):
        self.__from_json(json)

    def __from_json(self, node):
        assert node["__typename"] == "Offer"

        self.monetizationType = node["monetizationType"]
        self.presentationType = node["presentationType"]
        self.subtitleLanguages = node["subtitleLanguages"]
        self.audioLanguages = node["audioLanguages"]

        self.id = node["package"]["packageId"]
        self.providerClearName = node["package"]["clearName"]
        self.providertechnicalName = node["package"]["technicalName"]
        self.providerShortName = node["package"]["shortName"]
