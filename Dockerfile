FROM frictionlessdata/datapackage-pipelines

RUN pip install --no-cache-dir pipenv pew
RUN apk --update --no-cache add build-base python3-dev bash jq

COPY Pipfile /pipelines/
COPY Pipfile.lock /pipelines/
RUN pipenv install --system --deploy --ignore-pipfile && pipenv check

COPY static/ /pipelines/static
#COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY *.py /pipelines/
COPY *.yaml /pipelines/
COPY templates/ /pipelines/templates


#ENTRYPOINT ["/docker-entrypoint.sh"]
