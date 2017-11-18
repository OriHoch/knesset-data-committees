#!/usr/bin/env bash
[ "${UPV_ROOT}${UPV_WORKSPACE}" == "" ] && echo "Please run this script via ./upv.sh script" && exit 1

source "${UPV_ROOT}/functions.sh"
source "${UPV_WORKSPACE}/functions.sh"

if [ "${1}" == "--help" ] ; then
    echo 'Usage: ./upv.sh . dist_package [PACKAGE_NAME]'
    exit 1
fi

PACKAGE_NAME="${1:-`date +%Y-%m-%d-%H-%M`}"

info "Creating dist package \"${PACKAGE_NAME}\""

TEMPDIR=`mktemp -d`
PACKAGE_FILE="${TEMPDIR}/${PACKAGE_NAME}.tar.bz2"
tar -cjf "${PACKAGE_FILE}" dist

ls -lah "${PACKAGE_FILE}"
