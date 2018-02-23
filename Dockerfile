FROM orihoch/sk8s-pipelines:v0.0.3-b

RUN pip install --no-cache-dir pipenv pew
RUN apk --update --no-cache add build-base python3-dev bash jq

COPY Pipfile /pipelines/
COPY Pipfile.lock /pipelines/
RUN pipenv install --system --deploy --ignore-pipfile && pipenv check

COPY --from=gcr.io/uumpa-public/sk8s-pipelines:v0.0.3 /entrypoint.sh /entrypoint.sh

COPY static/ /pipelines/static
COPY *.py /pipelines/
COPY *.yaml /pipelines/
COPY templates/ /pipelines/templates
COPY *.sh /pipelines/

ENV PIPELINES_SCRIPT="cd /pipelines && (source ./pipelines_script.sh)"
ENV RUN_PIPELINE_CMD=run_pipeline
