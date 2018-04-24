# Knesset Data Committees Web App

Web app that shows data about Knesset committees generated from [knesset-data-pipelines](https://github.com/hasadna/knesset-data-pipelines)

The source for most of the data are the official [Knesset APIs](http://main.knesset.gov.il/Activity/Info/Pages/Databases.aspx)

Behind the scenes it uses a static build pipeline which generates html files and related assets that are then served statically.


## Installation

Install system dependencies, following works on recent Ubuntu:

```
sudo apt-get install libleveldb-dev python3.6 python3-pip python3.6-dev
sudo pip3 install pipenv
```

To install leveldb, try `sudo apt-get install libleveldb1v5` / `sudo apt-get install libleveldb1` or refer to [Level DB documentation](https://github.com/google/leveldb)

Install the app dependencies

```
pipenv install
```

Install some additional dependencies

```
pipenv shell
pip install --upgrade https://github.com/OriHoch/datapackage-pipelines/archive/cli-support-list-of-pipeline-ids.zip
pip install --upgrade https://github.com/hasadna/knesset-data-pipelines/archive/master.zip
```

Run the test to get the test data and make sure everything is installed properly

```
pipenv run ./test.sh
```


## Usage

Update the app dependencies

```
pipenv update
```

Activate the virtualenv

```
pipenv shell
```

Prepare the source data

```
dpp run ./download
dpp run ./join-meetings
dpp run ./download_members
```

Build the data in preparation for rendering

(You should edit pipeline-spec.yaml and uncomment some filters to limit the number of rows for rendering)

```
dpp run ./build
```

Render the meetings (ENABLE_LOCAL_CACHING saves the meeting files for quicker rebuild)

```
ENABLE_LOCAL_CACHING=1 dpp run ./render_meetings
```

Start a local dev server to view the generated files:

```
(cd dist; python3 -m http.server)
```


## Running using docker

If you have access to the required secrets and google cloud account, you can use the following command to run with all required dependencies:

```
docker run -d --rm --name postgresql -p 5432:5432 -e POSTGRES_PASSWORD=123456 postgres
docker build -t knesset-data-committees .
docker run -it -e DUMP_TO_STORAGE=1 \
               -e DUMP_TO_SQL=1 \
               -e DPP_DB_ENGINE=postgresql://postgres:123456@postgresql:5432/postgres \
               -v /path/to/google/secret/key:/secret_service_key \
               --link postgresql \
               knesset-data-committees
```
