from datapackage_pipelines.wrapper import ingest, spew
from template_functions import get_jinja_env
import logging, os, subprocess
from datetime import datetime
from template_functions import build_template, get_context
from constants import MEMBER_URL, POSITION_URL, MINISTRY_URL, FACTION_URL

def main():
    parameters, datapackage, resources = ingest()

    jinja_env = get_jinja_env()
    jinja_env.filters['datetime'] = datetimeformat

    all_mks = []
    for descriptor, resource in zip(datapackage["resources"], resources):
        for member in resource:
            build_template(jinja_env, "member_detail.html",
                           get_context({"first_name": member["mk_individual_first_name"],
                                        "last_name": member["mk_individual_name"],
                                        "photo": member["mk_individual_photo"],
                                        "positions": sortpositions(member["positions"]),
                                        "position_url": POSITION_URL,
                                        "ministry_url": MINISTRY_URL,
                                        "faction_url": FACTION_URL,
                                        "source_member_schema": descriptor["schema"],
                                        "source_member_row": member}),
                           MEMBER_URL.format(member_id=member["mk_individual_id"]))
            all_mks.append({"first_name": member["mk_individual_first_name"],
                            "last_name": member["mk_individual_name"],
                            "url": MEMBER_URL.format(member_id=member["mk_individual_id"])})
    build_template(jinja_env, "members_index.html",
                   get_context({"all_mks": sorted(all_mks, key=lambda mk: mk["first_name"])}), "members/index.html")
    if os.environ.get("SKIP_STATIC") != "1":
        subprocess.check_call(["mkdir", "-p", "dist"])
        subprocess.check_call(["cp", "-rf", "static", "dist/"])

    spew({}, [], {})

def sortpositions(positions):
    try:
        return sorted(positions, key=datekey, reverse=True)
    except KeyError:
        return positions

def datekey(position):
    key = "1970-01-01 00:00:00"

    if position["finish_date"]:
        key = position["finish_date"]
    elif position["start_date"]:
        key = position["start_date"]

    return datetime.strptime(key, '%Y-%m-%d %H:%M:%S')


def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime(format)

if __name__ == "__main__":
    main()
