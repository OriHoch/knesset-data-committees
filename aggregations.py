
def update_meeting_aggregations(aggregations, meeting, is_built=False, committee_id=None, knesset_num=None):
    stats = aggregations.setdefault("stats", {})
    stats.setdefault("total meetings built", 0)
    stats.setdefault("total meetings", 0)
    aggregations.setdefault("knesset_num", {})
    aggregations.setdefault("committee_id", {})
    stats["total meetings"] += 1
    if is_built:
        stats["total meetings built"] += 1
        if knesset_num not in aggregations["knesset_num"]:
            aggregations["knesset_num"][knesset_num] = knesset_num_stats = {"num_meetings": 0, "committee_ids": set()}
        else:
            knesset_num_stats = aggregations["knesset_num"][knesset_num]
        knesset_num_stats["num_meetings"] += 1
        knesset_num_stats["committee_ids"].add(committee_id)
        if committee_id not in aggregations["committee_id"]:
            aggregations["committee_id"][committee_id] = committee_id_stats = {"num_meetings": 0, "meetings": []}
        else:
            committee_id_stats = aggregations["committee_id"][committee_id]
        committee_id_stats["num_meetings"] += 1
        committee_id_stats["meetings"].append(meeting)


def update_committee_aggregations(aggregations, is_built=False):
    stats = aggregations.setdefault("stats", {})
    stats.setdefault("total committees built", 0)
    stats.setdefault("total committees", 0)
    stats["total committees"] += 1
    if is_built:
        stats["total committees built"] += 1
