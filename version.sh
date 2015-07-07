#!/bin/bash
ver=$(python -c "from dmsa import get_version; print get_version(True)")
lvl=$(python -c "from dmsa import __version_info__; print __version_info__['releaselevel']")
serial="${BUILD_NUM:-0}"
sha="${COMMIT_SHA1:-0}"
sha="${sha:0:8}"
if [ "${lvl}" != "final" ]; then
    ver="${ver}-${lvl}+${serial}.${sha}"
fi
echo "${ver}"
