# Knesset-Data-Committees Helm chart

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
