#!/usr/bin/env bash


RUN_PIPELINE_CMD="${RUN_PIPELINE_CMD:-dpp run}"


RES=0;


! (
    $RUN_PIPELINE_CMD ./download &&\
    $RUN_PIPELINE_CMD ./join-meetings &&\
    $RUN_PIPELINE_CMD ./download_members &&\
    $RUN_PIPELINE_CMD ./build &&\
    $RUN_PIPELINE_CMD ./render_meetings &&\
    $RUN_PIPELINE_CMD ./render_committees
) && RES=1


exit $RES
