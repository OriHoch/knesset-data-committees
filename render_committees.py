from datapackage_pipelines.wrapper import ingest, spew
import os, subprocess
from template_functions import build_template, get_jinja_env, get_context
from constants import COMMITTEE_DETAIL_URL, COMMITTEE_LIST_KNESSET_URL, MEMBER_URL, COMMITTEES_INDEX_URL
from committees_common import get_committee_name, get_meeting_path, get_meeting_topics, is_future_meeting, has_protocol


parameters, datapackage, resources = ingest()
stats = {
    "kns_committees": 0,
    "mk_individuals": 0,
    "meetings": 0,
}


kns_committee_descriptor = datapackage["resources"][0]
kns_committees = {}
for kns_committee in next(resources):
    kns_committees[int(kns_committee["CommitteeID"])] = kns_committee
    stats["kns_committees"] += 1


mk_individual_descriptor = datapackage["resources"][1]
for mk in next(resources):
    mk_id = mk["mk_individual_id"]
    for position in mk["positions"]:
        if position.get("CommitteeID") and position["CommitteeID"] in kns_committees:
            kns_committee = kns_committees[position["CommitteeID"]]
            kns_committee_mks = kns_committee.setdefault("mks", {})
            if position["position_id"] == 41:
                # chairperson role overrides other roles
                kns_committee_mks[mk_id] = dict(mk, committee_position="chairperson")
            elif mk_id not in kns_committee_mks:
                if position["position_id"] in [42, 66]:
                    kns_committee_mks[mk_id] = dict(mk, committee_position="member")
                elif position["position_id"] == 67:
                    kns_committee_mks[mk_id] = dict(mk, committee_position="replacement")
                elif position["position_id"] == 663:
                    kns_committee_mks[mk_id] = dict(mk, committee_position="watcher")
                else:
                    kns_committee_mks[mk_id] = dict(mk, committee_position="other")
    stats["mk_individuals"] += 1


meetings_descriptor = datapackage["resources"][2]


jinja_env = get_jinja_env()


def get_committee_meeting_contexts(committee):
    for meeting in sorted(committee["meetings"], key=lambda m:m["StartDate"], reverse=True):
        yield {"date_string": meeting["StartDate"].strftime("%d/%m/%Y"),
               "url": get_meeting_path(meeting),
               "title": get_meeting_topics(meeting),
               "is_future_meeting": is_future_meeting(meeting),
               "has_protocol": has_protocol(meeting)}


def get_committee_context(committee):
    return get_context({"source_committee_row": committee,
                        "source_committee_schema": kns_committee_descriptor["schema"],
                        "name": get_committee_name(committee),
                        "meetings": get_committee_meeting_contexts(committee),
                        "knesset_num": committee["KnessetNum"],
                        "committeelist_knesset_url": COMMITTEE_LIST_KNESSET_URL.format(num=committee["KnessetNum"]),
                        "member_url": MEMBER_URL,
                        "mks": sorted(committee.get("mks", {}).values(), key=lambda mk: mk["mk_individual_name"]),
                        })


def get_committee_list_context(committees, knesset_num):
    def committees_generator():
        for committee in committees:
            yield {"id": committee["CommitteeID"],
                   "name": get_committee_name(committee),
                   "url": COMMITTEE_DETAIL_URL.format(committee_id=committee["CommitteeID"]),
                   "num_meetings": len(committee["meetings"]),
                   }
    return get_context({"committees": sorted(committees_generator(), key=lambda c: c["name"]),
                        "knesset_num": knesset_num})


def get_committee_index_context(knesset_num_committees):
    def knesset_nums():
        for knesset_num, kns_committees in knesset_num_committees.items():
            num_meetings = 0
            for kns_committee in kns_committees:
                num_meetings += len(kns_committee.get("meetings", []))
            yield {"num": knesset_num,
                   "url": COMMITTEE_LIST_KNESSET_URL.format(num=knesset_num),
                   "num_committees": len(kns_committees),
                   "num_meetings": num_meetings}
    return get_context({"knesset_nums": sorted(knesset_nums(), key=lambda k: k["num"], reverse=True)})


all_meetings = {}
for meeting in next(resources):
    committee = kns_committees[meeting["CommitteeID"]]
    committee.setdefault("meetings", []).append(meeting)
    all_meetings[meeting["CommitteeSessionID"]] = meeting
    stats["meetings"] += 1


for meeting_stats in next(resources):
    all_meetings[meeting_stats["CommitteeSessionID"]]["num_speech_parts"] = meeting_stats["num_speech_parts"]


knesset_num_committees = {}
for kns_committee in kns_committees.values():
    knesset_num_committees.setdefault(kns_committee["KnessetNum"], []).append(kns_committee)
    build_template(jinja_env,
                   "committee_detail.html",
                   get_committee_context(kns_committee),
                   COMMITTEE_DETAIL_URL.format(committee_id=kns_committee["CommitteeID"]))


for knesset_num, kns_committees in knesset_num_committees.items():
    build_template(jinja_env,
                   "committee_list.html",
                   get_committee_list_context(kns_committees, knesset_num),
                   COMMITTEE_LIST_KNESSET_URL.format(num=knesset_num))


build_template(jinja_env,
               "committees_index.html",
               get_committee_index_context(knesset_num_committees),
               COMMITTEES_INDEX_URL)

if os.environ.get("SKIP_STATIC") != "1":
    subprocess.check_call(["mkdir", "-p", "dist"])
    subprocess.check_call(["cp", "-rf", "static", "dist/"])

spew(dict(datapackage, resources=[]), [], stats)
