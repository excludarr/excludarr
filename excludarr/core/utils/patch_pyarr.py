from typing import Any, Optional, Union
from pyarr import RadarrAPI, SonarrAPI
from pyarr.types import JsonObject, JsonArray
from requests import Response

# WARNING: This is a temporary fix until pyarr is updated


class PatchedSonarrAPI(SonarrAPI):
    # GET /episode
    def get_episode(
        self, id_: int, series: bool = False, season: int | None = None
    ) -> JsonObject:
        """Get episodes by ID or series

        Args:
            id_ (int): ID for Episode or Series.
            series (bool, optional): Set to true if the ID is for a Series. Defaults to false.

        Returns:
            JsonArray: List of dictionaries with items
        """  # noqa: E501
        params = {"seriesId": id_}
        if season is not None:
            params["seasonNumber"] = season

        return self._get(
            f"episode{'' if series else f'/{id_}'}",
            self.ver_uri,
            params=params if series else None,
        )

    # PUT /season/monitor
    def upd_season_monitor(
        self, season_ids: list[int], monitored: bool = True
    ) -> JsonArray:
        """Update episode monitored status

        Args:
            episode_ids (list[int]): All episode IDs to be updated
            monitored (bool, optional): True or False. Defaults to True.

        Returns:
            JsonArray: list of dictionaries containing updated records
        """
        return self._put(
            "season/monitor",
            self.ver_uri,
            data={"seasonIds": season_ids, "monitored": monitored},
        )

    # DELETE /series/{id}
    def del_series(
        self,
        id_: int,
        delete_files: bool = False,
        add_exclusion: Optional[bool] = None,
    ) -> Union[Response, JsonObject, dict[Any, Any]]:
        # added patch to add deleted series to list exclusions
        """Delete the series with the given ID

        Args:
            id_ (int): Database ID for series
            delete_files (bool, optional): If true series folder and files will be deleted. Defaults to False.
            add_exclusion (bool, optional): Add deleted series to List Exclusions. Defaults to None.

        Returns:
            dict: Blank dictionary
        """  # noqa: E501
        # File deletion does not work
        params: dict[str, Union[str, list[int], int]] = {}

        if delete_files:
            params["deleteFiles"] = delete_files
        if add_exclusion:
            params["addImportListExclusion"] = add_exclusion

        return self._delete(f"series/{id_}", self.ver_uri, params=params)


class PatchedRadarrAPI(RadarrAPI):

    def upd_movie(
        self,
        data: JsonObject,
        move_files: Optional[bool] = None,
    ) -> JsonObject:
        # removed leftover print

        """Updates a movie in the database.

        Args:
            data (JsonObject): Dictionary containing an object obtained from get_movie()
            move_files (Optional[bool], optional): Have radarr move files when updating. Defaults to None.

        Returns:
            JsonObject: Dictionary with updated record
        """  # noqa: E501
        params = {}
        if move_files is not None:
            params["moveFiles"] = move_files
        return self._put(
            "movie",
            self.ver_uri,
            data=data,
            params=params,
        )
