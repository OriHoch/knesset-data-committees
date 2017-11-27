import os, requests, json, logging


def load_kns_person_to_position_resource(resource, aggregations):
    # PersonToPositionID, PersonID, PositionID, KnessetNum, GovMinistryID, GovMinistryName, DutyDesc,
    # FactionID, FactionName, GovernmentNum, CommitteeID, CommitteeName, StartDate, FinishDate, IsCurrent,
    # LastUpdatedDate
    committees = aggregations["committees"]
    for row in resource:
        if row["CommitteeID"]:
            committees[int(row["CommitteeID"])].setdefault("person_ids", set()).add(int(row["PersonID"]))


def load_kns_person_resource(resource, aggregations):
    # PersonID, LastName, FirstName, GenderID, GenderDesc, Email, IsCurrent, LastUpdatedDate
    aggregations["kns_person"] = {int(row["PersonID"]): row for row in resource}


def load_kns_mksitecode_resource(resource, aggregations):
    # MKSiteCode, KnsID, SiteId
    aggregations["site_id_person_id"] = {}
    for row in resource:
        aggregations["site_id_person_id"][int(row["SiteId"])] = int(row["KnsID"])


def load_mk_individual_resource(resource, aggregations):
    site_id_person_id = aggregations["site_id_person_id"]
    kns_person = aggregations["kns_person"]
    mk_individual = aggregations["mk_individual"] = {}
    for row in resource:
        mk_individual[int(row["mk_individual_id"])] = row
        person_id = None
        if int(row["mk_individual_id"]) in site_id_person_id:
            person_id = int(site_id_person_id[int(row["mk_individual_id"])])
        else:
            logging.warning("person mismatch (name={} {}). old id is missing from mk site code table.".format(
                row["mk_individual_first_name_eng"],
                row["mk_individual_name_eng"]))
            logging.info("old mk id = {}, new id is unknown".format(row["mk_individual_id"]))
        if person_id:
            if person_id in kns_person:
                kns_person[person_id]["mk_individual"] = row
            else:
                logging.warning("person mismatch (name={} {}), new id is missing from kns_person.".format(
                    row["mk_individual_first_name_eng"],
                    row["mk_individual_name_eng"]))
                logging.info("old mk id = {}, new id = {}".format(row["mk_individual_id"], person_id))


def get_committee_persons(committee, aggregations):
    persons = []
    for person_id in committee.get("person_ids", []):
        person = aggregations["kns_person"][person_id]
        persons.append(person)
    return post_process_persons(persons, aggregations)


def get_meeting_attending_persons(speech_parts_list, aggregations):
    attended_persons = {}
    all_speech_parts = "  \n\n  ".join([p["header"]+"\n"+p["body"] for p in speech_parts_list])
    for person in aggregations["kns_person"].values():
        person_names = set()
        person_names.add(person["FirstName"]+" "+person["LastName"])
        if "mk_individual" in person:
            person_names.add(person["mk_individual"]["mk_individual_first_name"]+" "+person["mk_individual"]["mk_individual_name"])
        for person_name in person_names:
            if person_name in all_speech_parts:
                attended_persons[person["PersonID"]] = person
    return post_process_persons(attended_persons.values(), aggregations)


def post_process_persons(persons, aggregations):
    for person in persons:
        if "mk_individual" not in person:
            for mk, mk_name in zip(*get_mk_id_names(aggregations)):
                if mk_name == person["FirstName"]+" "+person["LastName"]:
                    if int(mk["id"]) in aggregations["mk_individual"]:
                        person["mk_individual"] = aggregations["mk_individual"][int(mk["id"])]
                    else:
                        raise Exception("Failed to find mk id {} in mk_individual".format(mk["id"]))
    return persons

# returns the open knesset mk site ids (corresponds to kns_mksitecode table)
# and the corresponding mk names and alternative names
def get_mk_id_names(aggregations):
    if "mk_id_names" not in aggregations:
        url = "https://oknesset.org/api/knesset-data/get_all_mk_names.json"
        if os.environ.get("ENABLE_LOCAL_CACHING") == "1":
            filepath = "data/cache/oknesset_mk_names.json"
            if not os.path.exists(filepath):
                if not os.path.exists(os.path.dirname(filepath)):
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "wb") as f:
                    f.write(requests.get(url).content)
            with open(filepath) as f:
                aggregations["mk_id_names"] = json.loads(f.read())
        else:
            aggregations["mk_id_names"] = json.loads(requests.get(url).content)
    return aggregations["mk_id_names"]

# returns open knesset mk details for the given mk site id (corresponds to kns_mksitecode table)
# def get_mk_details(mk_id, aggregations):
#     aggregations.setdefault("mk_details", {})
#     if mk_id not in aggregations:
#         url = "https://oknesset.org/api/v2/member/{}/?format=json".format(mk_id)
#         if os.environ.get("ENABLE_LOCAL_CACHING") == "1":
#             filepath = "data/cache/oknesset_member/{}.json".format(mk_id)
#             if not os.path.exists(filepath):
#                 if not os.path.exists(os.path.dirname(filepath)):
#                     os.makedirs(os.path.dirname(filepath), exist_ok=True)
#                 with open(filepath, "wb") as f:
#                     f.write(requests.get(url).content)
#             with open(filepath) as f:
#                 aggregations[mk_id] = json.loads(f.read())
#         else:
#             aggregations[mk_id] = json.loads(requests.get(url).content)
#     return aggregations[mk_id]
