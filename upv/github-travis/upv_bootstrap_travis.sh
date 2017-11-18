#!/usr/bin/env bash

echo "Installing system dependencies"
! sudo apt-get install jq uuid-runtime && exit 1

echo "Installing Docker"
! (curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - &&\
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" &&\
   sudo apt-get update &&\
   sudo apt-get -y install docker-ce) && exit 1

echo "Installing System Python dependencies"
! (sudo pip install --upgrade pip setuptools &&\
   sudo pip install python-dotenv pyyaml) && exit 1

echo "Creating .env file from travis vars"
touch "upv/github-travis/.env"
(
dotenv -f "upv/github-travis/.env" -qnever set "GITHUB_REPO_SLUG" "${GITHUB_REPO_SLUG}"
dotenv -f "upv/github-travis/.env" -qnever set "GITHUB_MASTER_BRANCH" "${GITHUB_MASTER_BRANCH}"
dotenv -f "upv/github-travis/.env" -qnever set "UPV_STRICT" "${UPV_STRICT}"
dotenv -f "upv/github-travis/.env" -qnever set "UPV_INTERACTIVE" "${UPV_INTERACTIVE}"
dotenv -f "upv/github-travis/.env" -qnever set "DOCKER_HUB_USER" "${DOCKER_HUB_USER}"
dotenv -f "upv/github-travis/.env" -qnever set "DOCKER_HUB_PASS" "${DOCKER_HUB_PASS}"
dotenv -f "upv/github-travis/.env" -qnever set "GITHUB_TOKEN" "${GITHUB_TOKEN}"
dotenv -f "upv/github-travis/.env" -qnever set "GIT_CONFIG_USER" "${GIT_CONFIG_USER}"
dotenv -f "upv/github-travis/.env" -qnever set "GIT_CONFIG_EMAIL" "${GIT_CONFIG_EMAIL}"
) >/dev/null

! ./upv.sh --debug --pull && echo "Failed upv pull" && exit 1
! ./upv.sh --debug . ls -lah && echo "Failed to bootstrap the upv environment" && exit 1

exit 0
