FROM frictionlessdata/datapackage-pipelines
RUN pip install --no-cache-dir pipenv pew
RUN apk --update --no-cache add build-base python3-dev bash jq libxml2 libxml2-dev git libxslt libxslt-dev curl \
                                libpq postgresql-dev openssl antiword
RUN apk --update --no-cache add linux-headers
COPY Pipfile /pipelines/
COPY Pipfile.lock /pipelines/
RUN pipenv install --system --deploy --ignore-pipfile
RUN apk --update --no-cache add python && pip install psycopg2-binary
RUN pip install --upgrade https://github.com/OriHoch/datapackage-pipelines/archive/cli-support-list-of-pipeline-ids.zip
RUN pip install --upgrade https://github.com/hasadna/knesset-data-pipelines/archive/master.zip
RUN cd / && wget -q https://storage.googleapis.com/pub/gsutil.tar.gz && tar xfz gsutil.tar.gz && rm gsutil.tar.gz
COPY boto.config /root/.boto
COPY static/ /pipelines/static
COPY *.py /pipelines/
COPY *.yaml /pipelines/
COPY templates/ /pipelines/templates
COPY *.sh /pipelines/
ENTRYPOINT ["/pipelines/pipelines_script.sh"]
