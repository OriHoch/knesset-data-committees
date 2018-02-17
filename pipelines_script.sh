#!/usr/bin/env bash

RUN_PIPELINE_CMD="${RUN_PIPELINE_CMD:-dpp run}"

RES=0;

! $RUN_PIPELINE_CMD ./download && RES=1
! $RUN_PIPELINE_CMD ./join-meetings && RES=1
! $RUN_PIPELINE_CMD ./download_members && RES=1
! $RUN_PIPELINE_CMD ./join-mks && RES=1
! $RUN_PIPELINE_CMD ./build && RES=1
! $RUN_PIPELINE_CMD ./render_meetings && RES=1
! $RUN_PIPELINE_CMD ./render_committees && RES=1

exit $RES
