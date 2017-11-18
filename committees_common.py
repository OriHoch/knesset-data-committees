# common committee functions - imported from other files
from template_functions import get_context
from speech_parts import get_speech_part_body, get_speech_parts
import os
from constants import MEETING_URL, COMMITTEE_LIST_KNESSET_URL, COMMITTEE_DETAIL_URL


def get_override_committee_ids(aggregations):
    override_ids = os.environ["OVERRIDE_COMMITTEE_IDS"].split(",") if os.environ.get("OVERRIDE_COMMITTEE_IDS") else []
    override_ids += aggregations["committee_id"].keys()
    override_ids = set(map(int, override_ids))
    return override_ids


def get_meeting_topics(meeting):
    return ", ".join(meeting["topics"]) if meeting["topics"] else ""


def get_meeting_path(meeting):
    return MEETING_URL.format(str(meeting["CommitteeSessionID"])[0],
                              str(meeting["CommitteeSessionID"])[1],
                              str(meeting["CommitteeSessionID"]))


def get_committee_meeting_contexts(committee, aggregations):
    committee_id = int(committee["CommitteeID"])
    if committee_id in aggregations["committee_id"]:
        meetings = aggregations["committee_id"][committee_id]["meetings"]
    else:
        meetings = []
    for meeting in meetings:
        yield {"date_string": meeting["StartDate"].strftime("%d/%m/%Y"),
               "url": get_meeting_path(meeting),
               "title": get_meeting_topics(meeting)}


def get_committee_name(committee):
    return committee["CategoryDesc"] if committee["CategoryDesc"] else committee["Name"]


def get_committee_detail_context(committee, descriptor, aggregations):
    aggregations["stats"]["total committees built"] += 1
    return get_context({"source_committee_row": committee,
                        "source_committee_schema": descriptor["schema"],
                        "name": get_committee_name(committee),
                        "meetings": get_committee_meeting_contexts(committee, aggregations),
                        "knesset_num": committee["KnessetNum"],
                        "committeelist_knesset_url": COMMITTEE_LIST_KNESSET_URL.format(num=committee["KnessetNum"])})

def get_meeting_context(meeting, committee, meetings_descriptor, committees_descriptor):
    speech_parts = list(get_speech_parts(meeting))
    context = get_context({"topics": get_meeting_topics(meeting),
                           "title": "ישיבה של {} בתאריך {}".format(committee["Name"],
                                                                   meeting["StartDate"].strftime("%d/%m/%Y")),
                           "committee_name": committee["Name"],
                           "meeting_datestring": meeting["StartDate"].strftime("%d/%m/%Y"),
                           "committee_url": COMMITTEE_DETAIL_URL.format(committee_id=committee["CommitteeID"]),
                           "knesset_num": committee["KnessetNum"],
                           "committeelist_knesset_url": COMMITTEE_LIST_KNESSET_URL.format(num=committee["KnessetNum"]),
                           "meeting_id": meeting["CommitteeSessionID"],
                           "speech_parts": speech_parts,
                           "speech_part_body": get_speech_part_body,
                           "source_meeting_schema": meetings_descriptor["schema"],
                           "source_meeting_row": meeting,
                           "source_committee_schema": committees_descriptor["schema"],
                           "source_committee_row": committee})
    return context
