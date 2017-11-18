from template_functions import build_template
import os
from committees_common import get_committee_detail_context, get_override_committee_ids
from constants import COMMITTEE_DETAIL_URL
from aggregations import update_committee_aggregations


def build_committee_templates(jinja_env, committees, descriptor, aggregations):
    override_ids = get_override_committee_ids(aggregations)
    for committee_id, committee in committees.items():
        if not os.environ.get("OVERRIDE_COMMITTEE_IDS") or int(committee_id) in override_ids:
            update_committee_aggregations(aggregations, is_built=True)
            build_template(jinja_env,
                           "committee_detail.html",
                           get_committee_detail_context(committee, descriptor, aggregations),
                           COMMITTEE_DETAIL_URL.format(committee_id=committee_id))
        else:
            update_committee_aggregations(aggregations, is_built=False)


