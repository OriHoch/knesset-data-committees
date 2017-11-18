#!/usr/bin/env bash
[ "${UPV_ROOT}${UPV_WORKSPACE}" == "" ] && echo "Please run this script via ./upv.sh script" && exit 1

source "${UPV_ROOT}/functions.sh"
source "${UPV_WORKSPACE}/functions.sh"

if [ "${1}" == "--help" ]; then
    echo 'Usage: ./upv.sh . provision_overrides \"[OVERRIDE_COMMITTEE_SESSION_IDS] [OVERRIDE_COMMITTEE_IDS] [OVERRIDE_KNESSET_NUMS] [OVERRIDE_ENABLE_LOCAL_CACHING]\"'
    exit 1
fi

OVERRIDE_COMMITTEE_SESSION_IDS="${1}"
OVERRIDE_COMMITTEE_IDS="${2}"
OVERRIDE_KNESSET_NUMS="${3}"
OVERRIDE_ENABLE_LOCAL_CACHING="${3}"

if [ "${OVERRIDE_COMMITTEE_SESSION_IDS}" == "" ]; then
    # a selection of meetings to test with, feel free to add more
    # the related committee pages will also be built for all these meetings
    OVERRIDE_COMMITTEE_SESSION_IDS="313032,313033,313034,313035,313036,2019185,2017980,2019005,2017521,2018001,2019190"
    OVERRIDE_COMMITTEE_SESSION_IDS+=",2019105,2019411,2019140,2018900,240190,102158,102161,65580,89096,97564,116155"
    OVERRIDE_COMMITTEE_SESSION_IDS+=",241127,330355,472030,472040,555144,98084,243406,565432,76653,88679,93436,93437"
    info "Overriding to default meetings: ${OVERRIDE_COMMITTEE_SESSION_IDS}"
else
    info "Overriding to meeting ids: ${OVERRIDE_COMMITTEE_SESSION_IDS}"
fi

if [ "${OVERRIDE_COMMITTEE_IDS}" == "" ]; then
    OVERRIDE_COMMITTEE_IDS="921,948,931,925,929,932,933,2035,926,937,922,1006,992"
    info "Overriding to default Committee IDs: ${OVERRIDE_COMMITTEE_IDS}"
else
    info "Overriding to Committee IDs: ${OVERRIDE_COMMITTEE_IDS}"
fi

if [ "${OVERRIDE_KNESSET_NUMS}" == "" ]; then
    OVERRIDE_KNESSET_NUMS="17,18,19,20"
    info "Overriding to default Knesset numbers: ${OVERRIDE_KNESSET_NUMS}"
else
    info "Overriding to Knesset numbers: ${OVERRIDE_KNESSET_NUMS}"
fi

if [ "${OVERRIDE_ENABLE_LOCAL_CACHING}" == "" ]; then
    OVERRIDE_ENABLE_LOCAL_CACHING="1"
fi
info "Enable local caching: ${OVERRIDE_ENABLE_LOCAL_CACHING}"

dotenv_set .env "OVERRIDE_COMMITTEE_SESSION_IDS" "${OVERRIDE_COMMITTEE_SESSION_IDS}"
dotenv_set .env "OVERRIDE_COMMITTEE_IDS" "${OVERRIDE_COMMITTEE_IDS}"
dotenv_set .env "OVERRIDE_KNESSET_NUMS" "${OVERRIDE_KNESSET_NUMS}"
dotenv_set .env "OVERRIDE_ENABLE_LOCAL_CACHING" "${OVERRIDE_ENABLE_LOCAL_CACHING}"
