import os, logging
from template_functions import build_template
from committees_common import get_meeting_context, get_meeting_path
from aggregations import update_meeting_aggregations


def build_meeting_templates(resource, committees, jinja_env, descriptor, committees_descriptor, aggregations):
    override_meeting_ids = list(map(int, os.environ["OVERRIDE_COMMITTEE_SESSION_IDS"].split(","))) if os.environ.get("OVERRIDE_COMMITTEE_SESSION_IDS") else None
    override_committee_ids = list(map(int, os.environ["OVERRIDE_COMMITTEE_IDS"].split(","))) if os.environ.get("OVERRIDE_COMMITTEE_IDS") else None
    override_knesset_nums = list(map(int, os.environ["OVERRIDE_KNESSET_NUMS"].split(","))) if os.environ.get("OVERRIDE_KNESSET_NUMS") else None

    logging.info("override_meeting_ids={}, ovverride_committee_ids={}, override_knesset_nums={}".format(override_meeting_ids, override_committee_ids, override_knesset_nums))

    for meeting in resource:
        if not override_meeting_ids or int(meeting["CommitteeSessionID"]) in override_meeting_ids:
            committee_id = int(meeting["CommitteeID"])
            committee = committees[committee_id]
            knesset_num = int(committee["KnessetNum"])

            if (
                (override_meeting_ids or not override_committee_ids or committee_id in override_committee_ids)
                and (override_meeting_ids or override_committee_ids or not override_knesset_nums or knesset_num in override_knesset_nums)
            ):
                update_meeting_aggregations(aggregations, meeting, True, committee_id, knesset_num)
                build_template(jinja_env,
                               "committeemeeting_detail.html",
                               get_meeting_context(meeting, committee, descriptor, committees_descriptor, aggregations),
                               get_meeting_path(meeting))

            else:
                update_meeting_aggregations(aggregations, meeting, is_built=False, committee_id=committee_id, knesset_num=knesset_num)
        else:
            update_meeting_aggregations(aggregations, meeting)
