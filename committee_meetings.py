import os
from template_functions import build_template
from committees_common import get_meeting_context, get_meeting_path


def update_meetings_aggregations(aggregations, committee_id, meeting):
    # top_meetings = aggregations["committee_id"][committee_id]["top_meetings"] + [meeting]
    # aggregations["committee_id"][committee_id]["top_meetings"] = sorted(top_meetings, key=lambda m: m["StartDate"],
    #                                                                     reverse=True)[:10]
    aggregations["committee_id"][committee_id]["meetings"].append(meeting)


def build_meeting_templates(resource, committees, jinja_env, descriptor, committees_descriptor, aggregations):
    for meeting in resource:
        if not os.environ.get("OVERRIDE_COMMITTEE_SESSION_IDS") or str(meeting["CommitteeSessionID"]) in os.environ["OVERRIDE_COMMITTEE_SESSION_IDS"].split(","):
            committee = committees[meeting["CommitteeID"]]
            aggregations["stats"]["total meetings built"] += 1
            knesset_num = int(committee["KnessetNum"])
            if knesset_num not in aggregations["knesset_num"]:
                aggregations["knesset_num"][knesset_num] = {"num_meetings": 0,
                                                            "committee_ids": set()}
            aggregations["knesset_num"][knesset_num]["num_meetings"] += 1
            aggregations["knesset_num"][knesset_num]["committee_ids"].add(meeting["CommitteeID"])
            committee_id = int(meeting["CommitteeID"])
            if committee_id not in aggregations["committee_id"]:
                aggregations["committee_id"][committee_id] = {"num_meetings": 0,
                                                              "meetings": []}
            aggregations["committee_id"][committee_id]["num_meetings"] += 1
            update_meetings_aggregations(aggregations, committee_id, meeting)
            build_template(jinja_env,
                           "committeemeeting_detail.html",
                           get_meeting_context(meeting, committee, descriptor, committees_descriptor),
                           get_meeting_path(meeting))
