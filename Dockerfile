FROM orihoch/sk8s-pipelines:v0.0.3-b

RUN pip install --no-cache-dir pipenv pew
RUN apk --update --no-cache add build-base python3-dev bash jq

COPY Pipfile /pipelines/
COPY Pipfile.lock /pipelines/
RUN pipenv install --system --deploy --ignore-pipfile && pipenv check

# temporary fix for dpp not returning correct exit code
# TODO: remove once datapackage-pipelines v1.5.4 is released
RUN pip install --upgrade https://github.com/OriHoch/datapackage-pipelines/archive/fix-exit-code.zip

COPY --from=orihoch/sk8s-pipelines:v0.0.3-d /entrypoint.sh /entrypoint.sh

COPY static/ /pipelines/static
#COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY *.py /pipelines/
COPY *.yaml /pipelines/
COPY templates/ /pipelines/templates
