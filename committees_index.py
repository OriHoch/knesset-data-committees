import os
from template_functions import build_template, get_context
from committees_common import get_override_committee_ids, get_committee_name
from constants import COMMITTEE_DETAIL_URL, COMMITTEE_LIST_KNESSET_URL, COMMITTEES_INDEX_URL


def get_committee_list_context(committees, knesset_num, aggregations):
    def committees_generator():
        override_ids = get_override_committee_ids(aggregations)
        for committee_id, committee in committees.items():
            if not os.environ.get("OVERRIDE_COMMITTEE_IDS") or int(committee_id) in override_ids:
                if committee.get("KnessetNum") and int(committee["KnessetNum"]) == int(knesset_num) and int(committee_id) in aggregations["committee_id"]:
                    yield {"id": committee_id,
                           "name": get_committee_name(committee),
                           "url": COMMITTEE_DETAIL_URL.format(committee_id=committee["CommitteeID"]),
                           "num_meetings": aggregations["committee_id"][int(committee_id)]["num_meetings"]}
    return get_context({"committees": sorted(committees_generator(), key=lambda c: c["name"]),
                        "knesset_num": knesset_num,
                        "aggregations": aggregations})



def build_committee_knessets_list_template(jinja_env, committees, aggregations):
    override_nums = os.environ["OVERRIDE_KNESSET_NUMS"].split(",") if os.environ.get("OVERRIDE_KNESSET_NUMS") else []
    override_nums += aggregations["knesset_num"].keys()
    override_nums = set(map(int, override_nums))
    for knesset_num, knesset_num_stats in aggregations["knesset_num"].items():
        if not os.environ.get("OVERRIDE_KNESSET_NUMS") or int(knesset_num) in override_nums:
            context = get_committee_list_context(committees, knesset_num, aggregations)
            if len(context["committees"]) > 0:
                build_template(jinja_env,
                               "committee_list.html",
                               context,
                               COMMITTEE_LIST_KNESSET_URL.format(num=knesset_num))

def build_committees_index_template(jinja_env, committees, aggregations):
    override_nums = os.environ["OVERRIDE_KNESSET_NUMS"].split(",") if os.environ.get("OVERRIDE_KNESSET_NUMS") else []
    override_nums += aggregations["knesset_num"].keys()
    override_nums = set(map(int, override_nums))
    def knesset_nums():
        for knesset_num, knesset_num_stats in aggregations["knesset_num"].items():
            if not os.environ.get("OVERRIDE_KNESSET_NUMS") or int(knesset_num) in override_nums:
                num_meetings = 0
                for committee_id, committee_stats in aggregations["committee_id"].items():
                    if int(committee_id) in map(int, knesset_num_stats["committee_ids"]):
                        num_meetings += committee_stats["num_meetings"]
                yield {"num": knesset_num,
                       "url": COMMITTEE_LIST_KNESSET_URL.format(num=knesset_num),
                       "num_committees": len(knesset_num_stats["committee_ids"]),
                       "num_meetings": num_meetings}
    context = get_context({"knesset_nums": sorted(knesset_nums(), key=lambda k: k["num"], reverse=True)})
    build_template(jinja_env,
                   "committees_index.html",
                   context,
                   COMMITTEES_INDEX_URL)
