from datapackage_pipelines.wrapper import ingest, spew
from dotenv import load_dotenv, find_dotenv
from template_functions import get_jinja_env

from committee_meetings import build_meeting_templates
from committees import build_committee_templates
from committees_index import build_committee_knessets_list_template, build_committees_index_template


load_dotenv(find_dotenv())


def main():
    parameters, datapackage, resources = ingest()
    stats = {}
    aggregations = {
        "stats": stats
    }
    jinja_env = get_jinja_env()
    committees = {}
    committees_descriptor = None
    for descriptor, resource in zip(datapackage["resources"], resources):
        if descriptor["name"] == "kns_committee":
            committees_descriptor = descriptor
            for committee in resource:
                committees[int(committee["CommitteeID"])] = committee
        elif descriptor["name"] == "kns_committeesession":
            build_meeting_templates(resource, committees, jinja_env, descriptor, committees_descriptor, aggregations)
            build_committee_templates(jinja_env, committees, committees_descriptor, aggregations)
            build_committee_knessets_list_template(jinja_env, committees, aggregations)
            build_committees_index_template(jinja_env, committees, aggregations)
    spew({}, [], stats)


if __name__ == "__main__":
    main()
