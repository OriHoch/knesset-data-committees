from datapackage_pipelines.wrapper import ingest, spew
from template_functions import get_jinja_env
import logging, os, subprocess
from datetime import datetime
from template_functions import build_template, get_context
from constants import MEMBER_URL, POSITION_URL, MINISTRY_URL, FACTION_URL

def main():
    parameters, datapackage, resources = ingest()

    jinja_env = get_jinja_env()
    jinja_env.filters['datetime'] = dateTimeFormat

    members = {}
    committees = {}

    for descriptor, resource in zip(datapackage["resources"], resources):

        if descriptor["name"] == "mk_individual":
            for member in resource:
                mkId = member["mk_individual_id"]
                members[mkId] = {
                    "mk_individual_id": mkId,
                    "first_name": member["mk_individual_first_name"],
                    "last_name": member["mk_individual_name"],
                    "photo": member["mk_individual_photo"],
                    "icon": getIcon(member["mk_individual_photo"]),
                    "positions": sortPositions(member["positions"]),
                    "position_url": POSITION_URL,
                    "ministry_url": MINISTRY_URL,
                    "faction_url": FACTION_URL,
                    "source_member_schema": descriptor["schema"],
                    "url": MEMBER_URL.format(member_id=mkId),
                    "source_member_row": member}

        elif descriptor["name"] == "kns_committeesession":
            for committee in resource:
                # aggregate statistics only if there is a protocol and mks
                if committee["text_file_name"] and committee["attended_mk_individual_ids"]:
                    knessetNum = committee["KnessetNum"]

                    if knessetNum not in committees:
                        committees[knessetNum] = 0
                    committees[knessetNum] += 1

                    for mkId in committee["attended_mk_individual_ids"]:
                        if mkId in members and isMember(members[mkId]["positions"], committee["StartDate"]):
                            if "counts" not in members[mkId]:
                                members[mkId]["counts"] = {}
                            if knessetNum not in members[mkId]["counts"]:
                                members[mkId]["counts"][knessetNum] = 0

                            members[mkId]["counts"][knessetNum] += 1

    for member in members.values():
        if "counts" in member:
            for knesset, count in member["counts"].items():
                percent = count / committees[knesset] * 100

                if "percents" not in member:
                    member["percents"] = {}
                member["percents"][knesset] = int(percent)

        build_template(jinja_env, "member_detail.html",
                       get_context(member),
                       MEMBER_URL.format(member_id=member["mk_individual_id"]))

    build_template(jinja_env, "members_index.html",
                   get_context({"members": sorted(members.values(), key=lambda mk: mk["first_name"])}), "members/index.html")

    if os.environ.get("SKIP_STATIC") != "1":
        subprocess.check_call(["mkdir", "-p", "dist"])
        subprocess.check_call(["cp", "-rf", "static", "dist/"])

    spew({}, [], {})

def getIcon(photo):
    return photo[:-4] + "-s" + photo[-4:]

def isMember(positions, startDate):

    if not startDate:
        return False

    for position in positions:
        if position["position_id"] == 54 and "start_date" in position:
            positionStartDate = datetime.strptime(position["start_date"], "%Y-%m-%d %H:%M:%S")

            if "finish_date" in position:
                positionEndDate = datetime.strptime(position["finish_date"], "%Y-%m-%d %H:%M:%S")
            else:
                positionEndDate = datetime.now()

            if positionStartDate <= startDate and positionEndDate >= startDate:
                return True

    return False

def sortPositions(positions):
    try:
        return sorted(positions, key=dateKey, reverse=True)
    except KeyError:
        return positions

def dateKey(position):
    key = "1970-01-01 00:00:00"

    if position["finish_date"]:
        key = position["finish_date"]
    elif position["start_date"]:
        key = position["start_date"]

    return datetime.strptime(key, "%Y-%m-%d %H:%M:%S")


def dateTimeFormat(value, format="%Y-%m-%d %H:%M:%S"):
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime(format)

if __name__ == "__main__":
    main()
