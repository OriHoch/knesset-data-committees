upv_sh_local_install() {
    info "Attempting to install locally, this may not always work"
    sudo apt-get install python3.6 python3.6-dev libleveldb-dev libleveldb1v5 &&\
    sudo pip3 install pipenv &&\
    pipenv install --skip-lock
}

upv_sh_local_init() {
    export SHELL=/bin/bash
    export UPV_BASH="pipenv shell"
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
}

static_files_build(){
    mkdir -p dist
    echo "Copying static files"
    cp -rf static dist/
    pipenv run dpp run ./build
}

static_files_watch_changes() {
    pipenv run when-changed *.py *.sh templates/*.html -c "${UPV_WORKSPACE}/upv.sh upv/static-files build %f"
}

serve_preflight() {
    test -d dist
}

serve_start() {
    cd dist && pipenv run python -m http.server "$@"
}
