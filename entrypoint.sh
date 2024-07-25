#!/bin/bash

general_fast_search="${GENERAL_FAST_SEARCH:-true}"
general_locale="${GENERAL_LOCALE:-en_US}"
general_providers="[${GENERAL_PROVIDERS:-'netflix'}]"
tmdb_api_key="${TMDB_API_KEY}"
radarr_url="${RADARR_URL:-http://localhost:7878}"
radarr_api_key="${RADARR_API_KEY:-secret}"
radarr_verify_ssl="${RADARR_VERIFY_SSL:-false}"
radarr_exclude="[${RADARR_EXCLUDE:-''}]"
radarr_exclude_tags="[${RADARR_EXCLUDE_TAGS:-''}]"
sonarr_url="${SONARR_URL:-http://localhost:8989}"
sonarr_api_key="${SONARR_API_KEY:-secret}"
sonarr_verify_ssl="${SONARR_VERIFY_SSL:-false}"
sonarr_exclude="[${SONARR_EXCLUDE:-''}]"
sonarr_exclude_tags="[${SONARR_EXCLUDE_TAGS:-''}]"
cron_mode="${CRON_MODE:-false}"

cat <<EOF >/etc/excludarr/excludarr.yml
general:
  fast_search: $general_fast_search
  locale: $general_locale
  providers: $general_providers

radarr:
  url: '$radarr_url'
  api_key: '$radarr_api_key'
  verify_ssl: $radarr_verify_ssl
  exclude: $radarr_exclude
  tags_to_exclude: $radarr_exclude_tags

sonarr:
  url: '$sonarr_url'
  api_key: '$sonarr_api_key'
  verify_ssl: $sonarr_verify_ssl
  exclude: $sonarr_exclude
  tags_to_exclude: $sonarr_exclude_tags

EOF

if [[ ! -z $TMDB_API_KEY ]]; then
  cat <<EOF >>/etc/excludarr/excludarr.yml
tmdb:
  api_key: '$tmdb_api_key'
EOF
fi

cat <<EOF >/bin/excludarr
#!/bin/bash
poetry run -C /app excludarr \$@
EOF

chmod +x /bin/excludarr

if [ "$cron_mode" = true ]; then
  if test -f "/etc/excludarr/crontab"; then
    cp /etc/excludarr/crontab /var/spool/cron/crontabs/root
    crond -l 8 -f
  else
    echo "No crontab file mounted! Please mount a valid crontab file at /etc/excludarr/crontab before running in cron mode!"
    exit 1
  fi
else
  excludarr $@
fi
