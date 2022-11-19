#!/bin/bash

# clash 启动
CLASH_WORKDIR=$(dirname $0)
cd $CLASH_WORKDIR

echo "CLASH_WORKDIR --> ${CLASH_WORKDIR}"

function clash_version {

    [ -f 'clash' ] &&  clash_version$(./clash -v | awk '{print $2}')
}

function install_clash_core {

    echo 'Install Clash Core ...'

    wget -q  https://release.dreamacro.workers.dev/latest/clash-linux-amd64-latest.gz && \
    gzip -d clash-linux-amd64-latest.gz && \
    mv clash-linux-amd64-latest clash && \
    chmod u+x clash && \
    echo "Installed Success ..." && return
    
    echo Installed Error .
    exit 1
}

install_clash_core