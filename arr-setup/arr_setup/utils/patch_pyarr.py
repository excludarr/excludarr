from typing import Optional
from pyarr import RadarrAPI, SonarrAPI
from pyarr.types import JsonObject


def __add_series(
    self,
    series: JsonObject,
    quality_profile_id: int,
    language_profile_id: int,
    root_dir: str,
    season_folder: bool = True,
    monitored: bool = True,
    ignore_episodes_with_files: bool = False,
    ignore_episodes_without_files: bool = False,
    search_for_missing_episodes: bool = False,
    tags: list[int] = [],
) -> JsonObject:
    """Adds a new series to your collection

    Note:
        if you do not add the required params, then the series wont function. some of these without the others can
        indeed make a "series". But it wont function properly in nzbdrone.

    Args:
        series (JsonObject): A series object from `lookup()`
        quality_profile_id (int): Database id for quality profile
        language_profile_id (int): Database id for language profile
        root_dir (str): Root folder location, full path will be created from this
        season_folder (bool, optional): Create a folder for each season. Defaults to True.
        monitored (bool, optional): Monitor this series. Defaults to True.
        ignore_episodes_with_files (bool, optional): Ignore any episodes with existing files. Defaults to False.
        ignore_episodes_without_files (bool, optional): Ignore any episodes without existing files. Defaults to False.
        search_for_missing_episodes (bool, optional): Search for missing episodes to download. Defaults to False.

    Returns:
        JsonObject: Dictionary of added record
    """
    if not monitored and series.get("seasons"):
        for season in series["seasons"]:
            season["monitored"] = False

    series["rootFolderPath"] = root_dir
    series["qualityProfileId"] = quality_profile_id
    series["languageProfileId"] = language_profile_id
    series["seasonFolder"] = season_folder
    series["monitored"] = monitored
    series["addOptions"] = {
        "ignoreEpisodesWithFiles": ignore_episodes_with_files,
        "ignoreEpisodesWithoutFiles": ignore_episodes_without_files,
        "searchForMissingEpisodes": search_for_missing_episodes,
    }
    series["tags"] = tags

    return self._post("series", self.ver_uri, data=series)


def __upd_movie(
    self,
    data: JsonObject,
    move_files: Optional[bool] = None,
) -> JsonObject:
    """Updates a movie in the database.

    Args:
        data (JsonObject): Dictionary containing an object obtained from get_movie()
        move_files (Optional[bool], optional): Have radarr move files when updating. Defaults to None.

    Returns:
        JsonObject: Dictionary with updated record
    """
    params = {}
    if move_files is not None:
        params["moveFiles"] = move_files
    return self._put(
        "movie",
        self.ver_uri,
        data=data,
        params=params,
    )


def patch():
    # for some reason `add_series` does not accept `tags` when adding a serie
    # even if the API supports it
    setattr(SonarrAPI, "add_series", __add_series)

    # there was a random print inside this function, now there is not :)
    setattr(RadarrAPI, "upd_movie", __upd_movie)
