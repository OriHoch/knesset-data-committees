from template_functions import build_template
import os
from committees_common import get_committee_detail_context, get_committee_name, get_override_committee_ids
from constants import COMMITTEE_DETAIL_URL


def build_committee_templates(jinja_env, committees, descriptor, aggregations):
    override_ids = get_override_committee_ids(aggregations)
    for committee_id, committee in committees.items():
        if not os.environ.get("OVERRIDE_COMMITTEE_IDS") or int(committee_id) in override_ids:
            build_template(jinja_env,
                           "committee_detail.html",
                           get_committee_detail_context(committee, descriptor, aggregations),
                           COMMITTEE_DETAIL_URL.format(committee_id=committee_id))


def get_committees(committees, knesset_num, aggregations):
    override_ids = get_override_committee_ids(aggregations)
    for committee_id, committee in committees.items():
        if not os.environ.get("OVERRIDE_COMMITTEE_IDS") or int(committee_id) in override_ids:
            if committee.get("KnessetNum") and int(committee["KnessetNum"]) == int(knesset_num):
                yield {"id": committee_id,
                       "name": get_committee_name(committee),
                       "url": COMMITTEE_DETAIL_URL.format(committee_id=committee["CommitteeID"])}
