from datapackage_pipelines.wrapper import ingest, spew
import logging


parameters, datapackage, resources = ingest()


kns_committees = {}
for kns_committee in next(resources):
    kns_committees[int(kns_committee["CommitteeID"])] = kns_committee


mk_individuals = {}
for mk_individual in next(resources):
    mk_individuals[int(mk_individual["mk_individual_id"])] = mk_individual


def get_meeting(meeting):
    meeting["committee"] = kns_committees[meeting["CommitteeID"]]


def get_resource():
    for meeting in next(resources):
        if meeting["CommitteeID"] in kns_committees:
            logging.info(meeting)
            yield get_meeting(meeting)


spew(dict(datapackage, resources=[datapackage["resources"][2]]), [get_resource()])
