# Development reference

This document will walk you through running excludarr and setting up the environment locally.

## Running locally

### With poetry (suggested way)

1. run `poetry install` in the root folder
2. write your config file and put it in one of the paths indicated in the README or pass it to excludarr by using the `--config <your config>` flag
3. run `poetry run excludarr` or just `excludarr` and add all the args you want to pass to excludarr eg: `poetry run excludarr --debug radarr exclude -a not-monitored`
4. done

### Docker

1. in the root folder run `docker build --tag=excludarr .`
2. run `docker run -it --rm excludarr:latest` and add all the args you want to pass to excludarr eg: `docker run -it --rm excludarr:latest --debug radarr exclude -a not-monitored`. NOTE: you also have pass to docker all the environment variables necessary to setup the config file for info check the README
3. done

## Running the testing environment

The testing environment is composed of a Radarr instance and a Sonarr instance, we also have `arr-setup` a tool to automatically populate both Radarr and Sonarr based on a config. You can run the environment both with or without `arr-setup`, if you don't run it you'll just have to add movies/series manually.

This whole environment can be run both through docker compose or by running each component by hand.

### Without `arr-setup`

Steps to run the environment:

1. run `docker compose up` (by default only Radarr and Sonarr will run)
2. done

With the default `docker-compose.yml` you can reach radarr on `http://localhost:7878` and sonarr on `http://localhost:8989`

### With `arr-setup`

Steps to run the environment:

1. write your config file and put it in the `arr_setup_config` volume that will be mounted. The name of the config should be `config.yml` and you can find an example config file in `arr-setup/.examples/arr-setup-example.yml`
2. run `docker compose --profile setup up`
3. make sure that the logs for `setup-arr` and `config_setup_arr` do not contain errors
4. done

With the default `docker-compose.yml` you can reach radarr on `http://localhost:7878` and sonarr on `http://localhost:8989`
