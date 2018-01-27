from datapackage_pipelines.wrapper import ingest, spew
from template_functions import get_jinja_env
from committee_meetings import build_meeting_templates
from committees import build_committee_templates
from committees_index import build_committee_knessets_list_template, build_committees_index_template
from members import load_kns_mksitecode_resource, load_kns_person_resource, load_mk_individual_resource, load_kns_person_to_position_resource
import logging, os, sys, subprocess
from collections import OrderedDict


def main():
    parameters, datapackage, resources = ingest()
    stats = {}
    aggregations = {
        "stats": stats
    }
    jinja_env = get_jinja_env()
    aggregations["committees"] = committees = OrderedDict()
    committees_descriptor = None
    site_id_person_id = {}
    for descriptor, resource in zip(datapackage["resources"], resources):
        # committees data
        if descriptor["name"] == "kns_committee":
            committees_descriptor = descriptor
            for committee in sorted(resource, key=lambda c: c["StartDate"], reverse=True):
                committees[int(committee["CommitteeID"])] = committee

        # members data, it's not a lot of data, so we just load it all into memory
        # TODO: use the new mk_individual joined data
        elif descriptor["name"] == "kns_persontoposition":
            load_kns_person_to_position_resource(resource, aggregations)
        elif descriptor["name"] == "kns_person":
            load_kns_person_resource(resource, aggregations)
        elif descriptor["name"] == "kns_mksitecode":
            load_kns_mksitecode_resource(resource, aggregations)
        elif descriptor["name"] == "mk_individual":
            load_mk_individual_resource(resource, aggregations)

        # main meetings stream
        # parses all the meetings and builds all the pages
        elif descriptor["name"] == "kns_committeesession":
            build_meeting_templates(sorted(resource, key=lambda m: m["StartDate"], reverse=True), committees, jinja_env, descriptor, committees_descriptor, aggregations)
            build_committee_templates(jinja_env, committees, committees_descriptor, aggregations)
            build_committee_knessets_list_template(jinja_env, committees, aggregations)
            build_committees_index_template(jinja_env, committees, aggregations)

        else:
            raise Exception("Unknown resource name {}".format(descriptor["name"]))

    if os.environ.get("SKIP_STATIC") != "1":
        subprocess.check_call(["mkdir", "-p", "dist"])
        subprocess.check_call(["cp", "-rf", "static", "dist/"])

    spew({}, [], stats)


if __name__ == "__main__":
    main()
