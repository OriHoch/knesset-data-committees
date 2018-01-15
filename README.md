# Knesset Data Committees Web App

Web app that shows data about Knesset committees generated from [knesset-data-pipelines](https://github.com/hasadna/knesset-data-pipelines)

The source for most of the data are the official [Knesset APIs](http://main.knesset.gov.il/Activity/Info/Pages/Databases.aspx)

Behind the scenes it uses a static build pipeline which generates html files and related assets that are then served statically.

## Installation

```
pipenv install
```

## Usage

Activate the virtualenv

```
pipenv shell
```

Download the source data from knesset-data-pipelines to data/committees

```
dpp run ./download
```

Install libleveldb1


```
sudo apt-get install libleveldb-dev libleveldb1
sudo apt-get install python3.6 python3-pip python3.6-dev libleveldb-dev libleveldb1v5
sudo pip3 install pipenv
```

Join the meeting resources (requires level db: `sudo apt-get install libleveldb-dev libleveldb1v5`)

```
dpp run ./join-meetings
```

Run the build pipeline on a limited set of meetings

```
ENABLE_LOCAL_CACHING=1 OVERRIDE_KNESSET_NUMS=20 dpp run ./build
```

By defeault the pipelines load fresh data from knesset minio, but for local development you can use a local cache by setting ENABLE_LOCAL_CACHING=1

The build pipeline also copies the static files, if you haven't modified them, you can set SKIP_STATIC=1

Use the following overrides to get partial data (you can modify the values):

```
OVERRIDE_KNESSET_NUMS=20,19,18
OVERRIDE_COMMITTEE_IDS=928,2043,930,944
OVERRIDE_COMMITTEE_SESSION_IDS=2006348,574541,2006678
```

You can also put the settings in a .env file and pipenv will automatically load them when you run `pipenv shell`

Start a local dev server to view the generated files:

```
(cd dist; python3 -m http.server)
```

