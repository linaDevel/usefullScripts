#!/bin/bash

set -xe

REMOTE="ssh://${USER}@review.lina-infra.ru:29418"
PROJECT="openstack"

for repo in $@; do
    TMPDIR=$(mktemp -d)
    git clone "https://github.com/${PROJECT}/${repo}" "${TMPDIR}" 2> /dev/null > /dev/null
    pushd ${TMPDIR} > /dev/null
    git remote add linadevel "${REMOTE}/${PROJECT}/${repo}"
    git push linadevel
    popd > /dev/null
    rm -rf ${TMPDIR}
done
