#!/usr/bin/env bash

export TEST_DATA=1

! RUN_PIPELINE_CMD="dpp run" ./pipelines_script.sh && echo pipelines script failed && exit 1

echo "Starting http server"
(cd dist; python3 -m http.server) &
sleep 2

! curl localhost:8000/committees/index.html | grep "committees/knesset-20.html" \
    && echo committees index page is missing link to knesset 20 && exit 1

! curl localhost:8000/committees/knesset-20.html | grep "committees/2026.html" \
    && echo committees knesset 20 page is missing link to committee 2026 && exit 1

! curl localhost:8000/committees/2026.html | grep "meetings/2/0/2021925.html" \
    && echo committee 2026 page is missing link to meeting 2021925 && exit 1

! curl localhost:8000/meetings/2/0/2021925.html | grep "speech-2021925-355" \
    && echo committee 2021925 page is missing speechpart 355 && exit 1

kill %1
sleep 2

echo Great Success!
exit 0
