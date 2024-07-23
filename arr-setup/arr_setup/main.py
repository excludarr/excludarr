from pyarr import RadarrAPI, SonarrAPI
from pyarr.base import BaseArrAPI
from pyarr.exceptions import PyarrBadRequest
import rich
import typer
import sys

from typing import Collection, Dict, List, Optional
from loguru import logger

from . import __version__


from .utils.config import Config

# pyarr patches
from .utils import patch_pyarr
patch_pyarr.patch()


app = typer.Typer()


def get_and_add_tags(
    client: BaseArrAPI, tags: List[str], is_radarr: bool = True
) -> List[int]:
    # hacky way to implement a singleton :)
    if isinstance(client, RadarrAPI):
        if not hasattr(get_and_add_tags, "tags_on_radarr"):
            setattr(get_and_add_tags, "tags_on_radarr", {})
            result_tags = client.get_tag()
            for i in result_tags:
                get_and_add_tags.tags_on_radarr[i["label"]] = i["id"]  # type: ignore  # noqa: E501

        tags_on_radarr_or_sonarr = get_and_add_tags.tags_on_radarr  # type: ignore  # noqa: E501
    elif isinstance(client, SonarrAPI):
        if not hasattr(get_and_add_tags, "tags_on_sonarr"):
            setattr(get_and_add_tags, "tags_on_sonarr", {})
            result_tags = client.get_tag()
            for i in result_tags:
                get_and_add_tags.tags_on_sonarr[i["label"]] = i["id"]  # type: ignore  # noqa: E501

        tags_on_radarr_or_sonarr = get_and_add_tags.tags_on_sonarr  # type: ignore  # noqa: E501
    else:
        raise Exception("client is instance of a class that is not supported")

    tag_ids: List[int] = []

    for tag in tags:
        if tag in tags_on_radarr_or_sonarr.keys():
            tag_ids.append(tags_on_radarr_or_sonarr[tag])
            continue

        logger.debug(f"Creating tag '{tag}'")

        new_tag = client.create_tag(tag)
        tags_on_radarr_or_sonarr[new_tag["label"]] = new_tag["id"]
        tag_ids.append(tags_on_radarr_or_sonarr[new_tag["label"]])

    return tag_ids


def add_movies(config: Config, ignore_unknown_tags: bool = True):

    if config.radarr_url is None:
        rich.print("No url for Radarr was provided, Skipping Radarr")
        return

    if config.radarr_api_key is None:
        rich.print("No API key for Radarr was provided, Skipping Radarr")
        return

    if config.radarr_movies is None:
        rich.print("Movie list for Radarr was empty")
        return

    radarr_client = RadarrAPI(config.radarr_url, config.radarr_api_key)

    # root_dir = radarr_client.get_root_folder()[0]["path"]  # type: ignore
    quality_profile_id = radarr_client.get_quality_profile()[0]["id"]

    logger.debug(f"got movies: {config.radarr_movies}")
    for movie in config.radarr_movies:
        logger.debug(f"{movie}")

        if "title" in movie:
            title = movie["title"]
        else:
            logger.debug("skipping entry, no title")
            continue

        logger.debug(f"Looking up {title}")
        movie_to_add = radarr_client.lookup_movie(term=title)[0]

        tag_labels_from_config: List[str] = movie.get("tags", [])

        tag_ids = get_and_add_tags(radarr_client, tag_labels_from_config)

        monitored: bool = movie.get("monitored", False)

        logger.debug(f"Adding {title}")
        try:
            radarr_client.add_movie(
                movie=movie_to_add,
                root_dir="/movies",
                quality_profile_id=quality_profile_id,
                monitored=monitored,
                search_for_movie=False,
                tags=tag_ids,
            )
            logger.debug(f"'{title}' added")

        except PyarrBadRequest:
            movie_to_update = radarr_client.get_movie(
                movie_to_add["tmdbId"], True
            )[
                0  # type: ignore
            ]  # type: ignore

            movie_to_update["monitored"] = monitored
            movie_to_update["tags"] = tag_ids

            radarr_client.upd_movie(movie_to_update)
            logger.debug(f"'{title}' altready on Radarr, updated")

    logger.debug("Done adding movies to Radarr")


def add_series(config: Config, ignore_unknown_tags: bool = True):

    if config.sonarr_url is None:
        rich.print("No url for Sonarr was provided, Skipping Radarr")
        return

    if config.sonarr_api_key is None:
        rich.print("No API key for Sonarr was provided, Skipping Radarr")
        return

    if config.sonarr_series is None:
        rich.print("Series list for Radarr was empty")
        return

    sonarr_client: SonarrAPI = SonarrAPI(
        config.sonarr_url, config.sonarr_api_key
    )

    # root_dir = radarr_client.get_root_folder()[0]["path"]  # type: ignore
    quality_profile_id = sonarr_client.get_quality_profile()[0]["id"]
    language_profile_id = sonarr_client.get_language_profile()[0]["id"]

    logger.debug(f"got series: {config.sonarr_series}")
    for serie in config.sonarr_series:
        logger.debug(f"{serie}")

        if "title" in serie:
            title = serie["title"]
        else:
            logger.debug("skipping entry, no title")
            continue

        logger.debug(f"Looking up {title}")
        serie_to_add = sonarr_client.lookup_series(term=title)[0]

        tag_labels_from_config: List[str] = serie.get("tags", [])

        tag_ids = get_and_add_tags(sonarr_client, tag_labels_from_config)

        monitored: bool = serie.get("monitored", False)

        logger.debug(f"Adding {title}")
        try:
            sonarr_client.add_series(
                series=serie_to_add,
                root_dir="/series",
                quality_profile_id=quality_profile_id,
                language_profile_id=language_profile_id,
                monitored=False,
            )
            logger.debug(f"'{title}' added")

        except PyarrBadRequest:
            logger.debug(f"'{title}' altready on Sonarr")
            
        # TODO: update episodes based on config
            
        serie_to_update = sonarr_client.get_series(
            serie_to_add["tvdbId"], True
        )[
            0  # type: ignore
        ]  # type: ignore

        serie_to_update["monitored"] = monitored
        serie_to_update["tags"] = tag_ids

        sonarr_client.upd_series(serie_to_update)

    logger.debug("Done adding movies to Radarr")


@app.command()
def setup():
    """
    Initializes the command. Reads the configuration.
    """
    logger.debug("Got update as subcommand")

    # Hacky way to get the current log level context
    loglevel = logger._core.min_level  # type: ignore

    logger.debug("Reading configuration file")

    # TODO: take config path as parameter to override the default ones
    config = Config()

    add_movies(config)
    add_series(config)


def version_callback(value: bool):
    if value:
        typer.echo(f"arr_setup: v{__version__}")
        raise typer.Exit()


def _setup_logging(debug):
    """
    Setup the log formatter for Excludarr
    """

    log_level = "INFO"
    if debug:
        log_level = "DEBUG"

    logger.remove()

    # create a debug file if we are in debug mode
    # this file will be cleared every time the program runs,
    # if you need it, save it before it's gone :)
    if debug:
        logger.add(
            "file.log",
            level=log_level,
            colorize=False,
            backtrace=True,
            diagnose=True,
            mode="w",
        )

    logger.add(
        sys.stdout,
        colorize=True,
        format="[{time:YYYY-MM-DD HH:mm:ss}] - <level>{message}</level>",
        level=log_level,
    )


@app.callback()
def main(
    debug: bool = False,
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback
    ),
):
    # Setup the logger
    _setup_logging(debug)

    # Logging
    logger.debug(f"Starting arr_setup v{__version__}")


def cli():
    app(prog_name="arr_setup")


if __name__ == "__main__":
    cli()
