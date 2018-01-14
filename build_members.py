from datapackage_pipelines.wrapper import ingest, spew
from template_functions import get_jinja_env
import logging, os, subprocess
from datetime import datetime
from template_functions import build_template
from constants import MEMBER_URL, POSITION_URL, MINISTRY_URL, FACTION_URL

def main():
    parameters, datapackage, resources = ingest()

    jinja_env = get_jinja_env()
    jinja_env.filters['datetime'] = datetimeformat

    for descriptor, resource in zip(datapackage["resources"], resources):
        for member in resource:
            build_template(jinja_env,
                           "member_detail.html",{
                                "first_name": member["mk_individual_first_name"],
                                "last_name": member["mk_individual_name"],
                                "photo": member["mk_individual_photo"],
                                "positions": sorted(member["positions"], key=lambda p: p["finish_date"], reverse=True),
                                "position_url": POSITION_URL,
                                "ministry_url":MINISTRY_URL,
                                "faction_url": FACTION_URL},
                           MEMBER_URL.format(member_id=member["mk_individual_id"]))

    if os.environ.get("SKIP_STATIC") != "1":
        subprocess.check_call(["mkdir", "-p", "dist"])
        subprocess.check_call(["cp", "-rf", "static", "dist/"])

    spew({}, [], {})

def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime(format)

if __name__ == "__main__":
    main()
