![License](https://img.shields.io/github/license/excludarr/excludarr)

# Excludarr

<blockquote>
❗ This project is a continuation of <a href=https://github.com/haijeploeg/excludarr>haijeploeg/excludarr</a> which became unmaintained and stopped working around October, 2023 due to <a href="https://github.com/haijeploeg/excludarr/issues/92">this issue</a>, which this project has corrected.  However, due to changes in the JustWatch API, the <mark style="background-color: #dddddd">&nbsp;sonarr&nbsp;</mark> command is disabled, until new API calls can be implemented in a subsequent update.  


</blockquote>
<br/>

Excludarr is a CLI that interacts with Radarr and Sonarr instances. It completely manages you library in Sonarr and Radarr to only consist out of movies and series that are not present on any of the configured streaming providers. Excludarr can also re monitor movies and series if it is not available anymore on any of the configured streaming providers. You can also configure to delete the already downloaded files of the excluded entry to keep your storage happy! 🎉

[![asciicast](https://asciinema.org/a/459503.svg)](https://asciinema.org/a/459503?autoplay=1)

## Prerequisites

- Python 3.6 or Docker
- If you have Sonarr: Sonarr V3 (version 2 is not working!)
- If you have Radarr: Radarr V3

## Installation

Installation of excludarr can be done using pip.

```bash
pip install excludarr
```

## Configuration

To configure the application make sure that one of the following files exists:

```bash
/etc/excludarr/excludarr.yml
~/.config/excludarr/excludarr.yml
~/.excludarr/config/excludarr.yml
~/.excludarr.yml
./.excludarr.yml
```

The application will read those configuration files in that order. So `./.excludarr.yml` will overwrite `/etc/excludarr/excludarr.yml`. For a full list of options and their description see [excludarr-example.yml](.examples/excludarr-example.yml) in this repository.

> NOTE: To get a full list of available providers in your country, execute `excludarr providers list` and copy the full name of the provider in your configuration.

## Radarr

The `radarr` subcommands manages the library in your configured Radarr instance. Check `excludarr radarr --help` for a full list of options.

### Exclude

To delete or disable monitoring of the movies in Radarr you can execute the `excludarr radarr exclude` command. You can determine to either delete the movie or change the status to not monitored. You can alo configure if you want to delete the associated files and to add an import exclusion to prevent future importing of the movie.

By default no files are being deleted, you have to set the `-d` flag. To make the command non-interactive you can pass the `-y` flag to auto accept the confirmation question. To show the progress of the process you can pass the `--progress` flag to get a nice progress bar! Read the help page of the command carefully to adjust the command to your needs.

```bash
$ excludarr radarr exclude -a delete -d -e
              ╷                                            ╷                ╷
 Release Date │ Title                                      │ Used Diskspace │ Streaming Providers
╶─────────────┼────────────────────────────────────────────┼────────────────┼─────────────────────────────────╴
 2021-11-04   │ Red Notice                                 │ 0.00GB         │ Netflix
 2021-10-13   │ The Last Duel                              │ 0.00GB         │ Apple iTunes
 2021-11-04   │ Amina                                      │ 0.00GB         │ Netflix
 2021-11-25   │ Apex                                       │ 12.00GB        │ Apple iTunes
 2021-11-25   │ A Boy Called Christmas                     │ 0.00GB         │ Netflix
 2012-06-27   │ The Amazing Spider-Man                     │ 0.00GB         │ Netflix, Apple iTunes
 2017-07-05   │ Spider-Man: Homecoming                     │ 7.50GB         │ Apple iTunes
 2021-10-22   │ The Harder They Fall                       │ 0.00GB         │ Netflix
 2021-12-02   │ Single All the Way                         │ 0.00GB         │ Netflix
 2021-05-19   │ F9                                         │ 0.00GB         │ Apple iTunes
 2021-07-28   │ The Suicide Squad                          │ 10.00GB        │ Apple iTunes
 2021-10-29   │ Army of Thieves                            │ 0.00GB         │ Netflix
 2021-08-09   │ PAW Patrol: The Movie                      │ 0.00GB         │ Apple iTunes
 2018-12-06   │ Spider-Man: Into the Spider-Verse          │ 20.00GB        │ Apple iTunes
 2002-05-01   │ Spider-Man                                 │ 0.00GB         │ Netflix, Apple iTunes
╶─────────────┼────────────────────────────────────────────┼────────────────┼─────────────────────────────────╴
              │                       Total Used Diskspace │ 49.50GB        │
              ╵                                            ╵                ╵
Are you sure you want to delete the listed movies? [y/n] (n): y
Succesfully deleted the movies from Radarr!
```

> NOTE: If you want to exclude any of the movies listed in the table, just copy the title and paste it in your configuration file under `radarr -> excludes`.

### Re-add

To re enable monitoring of not-monitored movies in Radarr that are not present anymore on any of the streaming providers, you can execute `excludarr radarr re-add`. This will lookup all movies that are not monitored anymore in Radarr and check if they are still available on the configured streaming providers. If there is no match, the status of the movie will change to monitored. This is handy if you remove a streaming provider from the configuration, or if the movie is being deleted from a streaming provider.

```bash
$ excludarr radarr re-add
              ╷
 Release Date │ Title
╶─────────────┼───────────────────────────────────────────╴
 2021-08-27   │ Vacation Friends
 2021-10-13   │ The Last Duel
 2021-09-01   │ Shang-Chi and the Legend of the Ten Rings
 2021-06-17   │ Luca
 2019-06-28   │ Spider-Man: Far From Home
 2021-11-12   │ Home Sweet Home Alone
 2021-07-07   │ Black Widow
 2021-07-22   │ Snake Eyes: G.I. Joe Origins
 2021-07-28   │ Jungle Cruise
 2020-08-04   │ Deathstroke: Knights & Dragons - The Movie
 2021-05-19   │ F9
 2021-07-28   │ The Suicide Squad
 2021-08-09   │ PAW Patrol: The Movie
 2021-09-03   │ Zone 414
 2021-05-26   │ Cruella
 2021-07-15   │ Space Jam: A New Legacy
 2021-03-24   │ Godzilla vs. Kong
              ╵
Are you sure you want to re monitor the listed movies? [y/n] (n): y
Succesfully changed the status of the movies listed in Radarr to monitored!
```

> NOTE: If you want to exclude any of the movies listed in the table, just copy the title and paste it in your configuration file under `radarr -> excludes`.

## Sonarr

The `sonarr` subcommands manages the library in your configured Sonarr instance. Check `excludarr sonarr --help` for a full list of options.

### Exclude

To delete or disable monitoring of the series in Sonarr you can execute the `excludarr sonarr exclude` command. You can determine to either delete the serie or change the status to not monitored. You can alo configure if you want to delete the associated files. Excludarr will exclude the whole serie, the season(s) or individually episodes.

If you use the delete action (`excludarr sonarr exclude -a delete`) it will only delete the serie if the serie is ended and all seasons are streaming on a configured streaming service. A few examples with Netflix as a streaming provider.

- **Serie A** has a total of 5 seasons and has ended. If all 5 seasons are found on Netflix it will delete the serie from Sonarr.
- **Serie B** has a total of 4 seasons and it still continueing (season 5 will be released next year). If all 4 seasons are found on Netflix it will disable the monitoring of all 4 seasons, but it will **not** delete the whole serie from Sonarr.
- **Serie C** has a total of 6 seasons and has ended. If only 5 seasons are found on Netflix, Excludarr will disable monitoring of the 5 seasons and will **not** delete the serie from Sonarr.

By default no files are being deleted, you have to set the `-d` flag. To make the command non-interactive you can pass the `-y` flag to auto accept the confirmation question. To show the progress of the process you can pass the `--progress` flag to get a nice progress bar! Read the help page of the command carefully to adjust the command to your needs.

```bash
excludarr sonarr exclude -a delete -d
              ╷                                             ╷                ╷                                             ╷                                             ╷                    ╷
 Release Year │ Title                                       │ Used Diskspace │ Seasons                                     │ Episodes                                    │ Providers          │ Ended
╶─────────────┼─────────────────────────────────────────────┼────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────────────┼────────────────────┼──────╴
 2008         │ Breaking Bad                                │ 454.00GB       │ Season 1, Season 2, Season 3, Season 4,     │                                             │ Netflix            │ Yes
              │                                             │                │ Season 5                                    │                                             │                    │
 2010         │ The Walking Dead                            │ 0.00GB         │ Season 1, Season 2, Season 3, Season 4,     │                                             │ Netflix            │ No
              │                                             │                │ Season 5, Season 6, Season 7, Season 8,     │                                             │                    │
              │                                             │                │ Season 9, Season 10                         │                                             │                    │
 2016         │ Stranger Things                             │ 0.00GB         │ Season 1, Season 2, Season 3                │                                             │ Netflix            │ No
 2012         │ Arrow                                       │ 0.00GB         │ Season 1, Season 2, Season 3, Season 4,     │                                             │ Netflix            │ Yes
              │                                             │                │ Season 5, Season 6, Season 7, Season 8      │                                             │                    │
 2004         │ Lost                                        │ 0.00GB         │ Season 1, Season 2, Season 3, Season 4,     │                                             │ Videoland          │ Yes
              │                                             │                │ Season 5, Season 6                          │                                             │                    │
 2013         │ House of Cards (US)                         │ 0.00GB         │ Season 1, Season 2, Season 3, Season 4,     │                                             │ Netflix            │ Yes
              │                                             │                │ Season 5, Season 6                          │                                             │                    │
 2011         │ Suits                                       │ 30.00GB        │ Season 1, Season 2, Season 3, Season 4,     │                                             │ Netflix            │ Yes
              │                                             │                │ Season 5, Season 6, Season 7, Season 8,     │                                             │                    │
              │                                             │                │ Season 9                                    │                                             │                    │
 2013         │ Vikings                                     │ 100.00GB       │ Season 1, Season 2, Season 3, Season 4,     │                                             │ Netflix            │ Yes
              │                                             │                │ Season 5, Season 6                          │                                             │                    │
 2014         │ The Flash (2014)                            │ 0.00GB         │ Season 1, Season 2, Season 3, Season 4,     │ S08E01, S08E02, S08E03, S08E04, S08E05      │ Netflix            │ No
              │                                             │                │ Season 5, Season 6, Season 7                │                                             │                    │
 2013         │ Orange Is the New Black                     │ 0.00GB         │ Season 1, Season 2, Season 3, Season 4,     │                                             │ Netflix            │ Yes
              │                                             │                │ Season 5, Season 6, Season 7                │                                             │                    │
 2011         │ Black Mirror                                │ 0.00GB         │ Season 1, Season 2, Season 3, Season 4,     │                                             │ Netflix            │ Yes
              │                                             │                │ Season 5                                    │                                             │                    │
 2013         │ Rick and Morty                              │ 0.00GB         │ Season 1, Season 2, Season 3, Season 4,     │                                             │ Netflix            │ No
              │                                             │                │ Season 5                                    │                                             │                    │
 2005         │ The Office (US)                             │ 15.00GB        │ Season 1, Season 2, Season 3, Season 4,     │                                             │ Netflix, Videoland │ Yes
              │                                             │                │ Season 5, Season 6, Season 7, Season 8,     │                                             │                    │
              │                                             │                │ Season 9                                    │                                             │                    │
 2010         │ Spartacus                                   │ 30.00GB        │ Season 1, Season 3                          │ S02E01, S02E02, S02E03, S02E04, S02E05,     │ Netflix            │ Yes
              │                                             │                │                                             │ S02E06                                      │                    │
 2017         │ Dark                                        │ 0.00GB         │ Season 1, Season 2, Season 3                │                                             │ Netflix            │ Yes
╶─────────────┼─────────────────────────────────────────────┼────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────────────┼────────────────────┼──────╴
              │                        Total Used Diskspace │ 629.00GB       │                                             │                                             │                    │
              ╵                                             ╵                ╵                                             ╵                                             ╵                    ╵
Are you sure you want to delete the listed series? [y/n] (n): y
Succesfully deleted the series and/or changed the status of serveral seasons and episodes listed in Sonarr to not monitored!
```

> NOTE: If you want to exclude any of the series listed in the table, just copy the title and paste it in your configuration file under `sonarr -> excludes`.

### Re-add

To re enable monitoring of not-monitored series in Sonarr that are not present anymore on any of the streaming providers, you can execute `excludarr sonarr re-add`. This will lookup all series/seasons/episodes that are not monitored anymore in Sonarr and check if they are still available on the configured streaming providers. If there is no match, the status of the serie will change to monitored. This is handy if you remove a streaming provider from the configuration, or if the movie is being deleted from a streaming provider.

```bash
excludarr sonarr re-add
              ╷                                                  ╷                                                             ╷                                                              ╷
 Release Year │ Title                                            │ Seasons                                                     │ Episodes                                                     │ Ended
╶─────────────┼──────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┼──────╴
 2010         │ The Walking Dead                                 │ Season 1, Season 2, Season 3, Season 4, Season 5, Season 6, │                                                              │ No
              │                                                  │ Season 7, Season 8, Season 9, Season 10                     │                                                              │
 2016         │ Stranger Things                                  │ Season 1, Season 2, Season 3                                │                                                              │ No
              │                                                  │ Season 7, Season 8                                          │                                                              │
 2004         │ Lost                                             │ Season 1, Season 2, Season 3, Season 4, Season 5, Season 6  │                                                              │ Yes
 2011         │ Suits                                            │ Season 1, Season 2, Season 3, Season 4, Season 5, Season 6, │                                                              │ Yes
              │                                                  │ Season 7, Season 8, Season 9                                │                                                              │
 2014         │ The Flash (2014)                                 │ Season 1, Season 2, Season 3, Season 4, Season 5, Season 6, │ S08E01, S08E02, S08E03, S08E04, S08E05                       │ No
              │                                                  │ Season 7                                                    │                                                              │
 2013         │ Orange Is the New Black                          │ Season 1, Season 2, Season 3, Season 4, Season 5, Season 6, │                                                              │ Yes
              │                                                  │ Season 7                                                    │                                                              │
 2013         │ Rick and Morty                                   │ Season 1, Season 2, Season 3, Season 4, Season 5            │                                                              │ No
 2005         │ The Office (US)                                  │ Season 1, Season 2, Season 3, Season 4, Season 5, Season 6, │                                                              │ Yes
              │                                                  │ Season 7, Season 8, Season 9                                │                                                              │
 1997         │ South Park                                       │ Season 1, Season 2, Season 18, Season 19, Season 20, Season │                                                              │ No
              │                                                  │ 21                                                          │                                                              │
 2013         │ The Blacklist                                    │ Season 1, Season 2, Season 3, Season 4, Season 5, Season 6, │ S09E01, S09E02, S09E03                                       │ No
              │                                                  │ Season 7, Season 8                                          │                                                              │
 2015         │ Better Call Saul                                 │ Season 1, Season 2, Season 3, Season 4, Season 5            │                                                              │ No
 2014         │ Gotham                                           │ Season 1, Season 2, Season 4, Season 5                      │ S03E01, S03E02, S03E03, S03E04, S03E05, S03E06, S03E07,      │ Yes
              │                                                  │                                                             │ S03E08, S03E09, S03E10, S03E11, S03E12, S03E13, S03E14,      │
              │                                                  │                                                             │ S03E15, S03E16, S03E17, S03E18, S03E19, S03E20, S03E21       │
 2005         │ Avatar: The Last Airbender                       │ Season 1, Season 2, Season 3                                │                                                              │ Yes
 2014         │ Fargo                                            │ Season 1, Season 2, Season 3, Season 4                      │                                                              │ No
              ╵                                                  ╵                                                             ╵                                                              ╵
Are you sure you want to re monitor the listed series? [y/n] (n): y
Succesfully changed the status of the series listed in Sonarr to monitored!
```

> NOTE: If you want to exclude any of the series listed in the table, just copy the title and paste it in your configuration file under `sonarr -> excludes`.

## Docker

To use this setup using Docker, you can use the `haijeploeg/excludarr` container. You can use the following environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| GENERAL_FAST_SEARCH | true | Enable or disable fast search, can be `true` or `false`. |
| GENERAL_LOCALE | en_US | The locale to use, can also be a two letter country code. |
| GENERAL_PROVIDERS | Netflix | Comma seperated list of providers. e.g. `GENERAL_PROVIDERS=netflix, amazon prime video`. |
| TMDB_API_KEY | - | Your TMDB API key. This setting is optional and only used in fallback scenario's. |
| RADARR_URL | http://localhost:7878 | The Radarr URL. |
| RADARR_API_KEY | secret | Your Radarr API Key. |
| RADARR_VERIFY_SSL | false | To enable SSL verify, can be `true` or `false`. |
| RADARR_EXCLUDE | - | Comma seperated list of movies to exclude in the process of Excludarr, e.g. `RADARR_EXCLUDE=The Matrix, F9`. |
| SONARR_URL | http://localhost:8989 | The Sonarr URL. |
| SONARR_API_KEY | secret | Your Sonarr API Key. |
| SONARR_VERIFY_SSL | false | To enable SSL verify, can be `true` or `false`. |
| SONARR_EXCLUDE | - | Comma seperated list of series to exclude in Excludarr, e.g. `SONARR_EXCLUDE=Breaking Bad, Game of Thrones`. |
| CRON_MODE | false | Wether to run the docker container using cron. This is useful for docker-compose. |

You can put those variables in a env file (e.g. `excludarr.env`) and use it in a command (recommended way). Look the [docker_example.env](.examples/docker_example.env) for an example. If you have set your variables properly, you can execute excludarr in docker by just adding the command and paramaters at the end of the docker command. Example:

```bash
docker run -it --rm --env-file excludarr.env haijeploeg/excludarr:latest radarr exclude -a delete -d -e --progress
docker run -it --rm --env-file excludarr.env haijeploeg/excludarr:latest sonarr exclude -a not-monitored
```

### Docker compose

Excludarr can run in cron mode using docker-compose. Using this method the container keeps running and wakes up when you want to run a scheduled command. To use this method you can create a [crontab](.examples/crontab) file and mount it to `/etc/excludarr/crontab` in the container. Make sure you run the command unattended (with the `-y` flag!)

```bash
$ cat crontab

# minute    hour    day   month   weekday   command
0           1       *     *       *         excludarr sonarr exclude -a delete -d -e -y
0           2       *     *       *         excludarr radarr exclude -a delete -d -e -y
```

Your docker-compose file can look like [this](.examples/docker-compose-example.yml). Make sure you set the `CRON_MODE` environment setting!

```bash
$ cat docker-compose.yml

version: "3"
services:
  excludarr:
    image: haijeploeg/excludarr
    container_name: excludarr
    environment:
      - GENERAL_FAST_SEARCH=true
      - GENERAL_LOCALE=en_NL
      - GENERAL_PROVIDERS=netflix, amazon prime video
      - RADARR_URL=http://radarr.example.com:7878
      - RADARR_API_KEY=secret
      - RADARR_VERIFY_SSL=false
      - SONARR_URL=http://sonarr.example.com:8989
      - SONARR_API_KEY=secret
      - SONARR_VERIFY_SSL=false
      - SONARR_EXCLUDE="Queen of the South, Breaking Bad"
      - CRON_MODE=true
    volumes:
      - ./crontab:/etc/excludarr/crontab
    restart: unless-stopped
```

With the above configuration the container will execute `excludarr sonarr exclude -a delete -d -e -y` every day at 01:00 and `excludarr radarr exclude -a delete -d -e -y` every day at 02:00.

## FAQ

Below are some frequently asked questions. Please look if your question is listed below before you submit an issue.

##

**Q:** I used the `--legacy` flag before, where can I find it in excludarr v1.0.0?

**A:** Excludarr will now automatically fall back to the legacy delete option if a bulk delete is not possible.

##

**Q:** Where is the `check` command?

**A:** The check command has been replaced by `re-add`.

##

**Q:** When excluding series there are no seasons or episodes displayed, what will excludarr do?

**A:** When there are no seasons and episodes displayed this means that excludarr will disable monitoring of the serie if the serie is not ended yet. When a serie is ended and the action was delete, Excludarr will delete the whole serie. When a serie is ended and the action is not-monitored, Excludarr will disable monitoring of the whole serie.

##

**Q:** Can I also exclude movies and series from being processed by Excludarr?

**A:** Yes, by using the `exclude` setting in the configuration file. You can set the `exclude` setting under the `radarr` and `sonarr` configuration section. You can see the example [excludarr-example.yml](.examples/excludarr-example.yml) file in this repo.

##

**Q:** How can I know what providers I can use in the configuration file?

**A:** You can list all the available providers for your specific locale using the `excludarr providers list` command. This should give you a list of all the available providers. Simply copy the full name and insert it in the configuration file.

##

**Q:** Does excludarr still support Sonarr V2?

**A:** No, Sonarr V2 is EOL (End Of Life) and therefor not supported by Excludarr. Please upgrade to Sonarr V3 by reading the [upgrade guide](https://forums.sonarr.tv/t/v3-is-now-officially-stable-v2-is-eol/27858)

## License

The project is [licensed](LICENSE) under [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.html) or later.

This project is a fork of this [original project](https://github.com/haijeploeg/excludarr), where you can find its [original MIT license](https://github.com/haijeploeg/excludarr/blob/main/LICENSE).  A copy of the original license is also included in this repository in [LICENSE.old](LICENSE.old)
