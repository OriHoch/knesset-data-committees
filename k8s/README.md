# Knesset-Data-Committees Helm chart

Currently the committees-pipelines pod is deployed on the knesset data cluster

If you haven't made any changes in the code and just want to re-build the pages start a new node pool called "committee-pipelines" g1-small and the deployment will automatically start the pods on it

## Installation

Provision the required resources to upload to google storage

```
export CLOUDSDK_CORE_PROJECT="hasadna-oknesset"
export STORAGE_BUCKET_NAME="knesset-data-committees"
export SERVICE_ACCOUNT_NAME="committees-storage"
export SERVICE_ACCOUNT_ID="${SERVICE_ACCOUNT_NAME}@${CLOUDSDK_CORE_PROJECT}.iam.gserviceaccount.com"

# Google Storage Bucket
gsutil mb "gs://${STORAGE_BUCKET_NAME}"

# Set as public
gsutil acl ch -R -u AllUsers:R gs://${STORAGE_BUCKET_NAME}

# Service account
gcloud iam service-accounts create "${SERVICE_ACCOUNT_NAME}"

# create the private key and store in kuberenetes secret
gcloud iam service-accounts keys create "--iam-account=${SERVICE_ACCOUNT_ID}" "secret_key"
KEY=`cat secret_key | base64 -w0`
rm secret_key
kubectl create secret generic committees-pipelines --from-literal=COMMITTEES_STORAGE_SERVICE_ACCOUNT_B64_KEY=${KEY}

# set admin permissions for the service account to the bucket
gsutil iam ch -d "serviceAccount:${SERVICE_ACCOUNT_ID}" "gs://${STORAGE_BUCKET_NAME}"
gsutil iam ch "serviceAccount:${SERVICE_ACCOUNT_ID}:objectCreator,objectViewer,objectAdmin" "gs://${STORAGE_BUCKET_NAME}"
```

## Deployment

Following commands assume you have properly configured and authenticated knesset-data-pipelines installation as sibling to this repo

Build

```
docker-compose build pipelines
```

Tag and push

```
DOCKER_USER=orihoch
DOCKER_TAG=`date +%y-%m-%d_%H-%M-%S`
docker tag knesset-data-committees "${DOCKER_USER}/knesset-data-committees:${DOCKER_TAG}"
docker push "orihoch/knesset-data-committees:${DOCKER_TAG}"
```

Update chart values

```
../knesset-data-pipelines/bin/update_yaml.py '{"image": "'"${DOCKER_USER}"'/knesset-data-committees:'"${DOCKER_TAG}"'"}' k8s/values.yaml
```

Deploy

```
export K8S_ENVIRONMENT=production
(cd ../knesset-data-pipelines && bin/k8s_upgrade_chart.sh knesset-data-committees ../knesset-data-committees/k8s)
```

(on first installation add the `--install` argument)

## Updating on Open Knesset

**The path on gs was changed, now dist is at the root of the bucket - need to modify the following instructions accordingly**

Install gcloud tools - used to sync the committees dist directory

(It runs interactively and might ask some questions - you can accept all default)

```
ssh oknesset-web1 'curl https://sdk.cloud.google.com | bash'
ssh oknesset-web2 'curl https://sdk.cloud.google.com | bash'
```

Authenticate and sync the files - repeat the same for both oknesset-web1 and oknesset-web2

Will take some time, can be done in parallel on both servers

```
ssh oknesset-web1
source google-cloud-sdk/path.bash.inc
gcloud auth login
sudo mkdir -p /oknesset_web/committees/dist
sudo chown -R $USER /oknesset_web/committees
gsutil -m rsync -r gs://knesset-data-committees/dist /oknesset_web/committees/dist
```

Once sync is done, [Open Knesset v4.7.0](https://github.com/hasadna/Open-Knesset/releases/tag/v4.7.0) will pick it up and serve it at https://oknesset.org/committees/index.html
