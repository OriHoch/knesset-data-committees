from datapackage_pipelines.wrapper import ingest, spew
from template_functions import get_jinja_env
import logging, os, subprocess
from datetime import datetime
from template_functions import build_template, get_context
from constants import FACTION_HOME_URL, FACTION_URL, MEMBER_URL


def main():
    parameters, datapackage, resources = ingest()

    jinja_env = get_jinja_env()

    members = {}
    factions = {}
    knessets = {}

    for descriptor, resource in zip(datapackage["resources"], resources):
        if descriptor["name"] == "members":
            for member in resource:
                members[member["mk_individual_id"]] = member
        elif descriptor["name"] == "positions":
            for position in resource:
                if position["object_type"] == "faction":
                    factions[position["object_id"]] = {
                        "faction_num": position["object_id"],
                        "faction_name": position["object_name"],
                        "mks": []
                    }
                    for id in position["mk_individual_ids"]:
                        factions[position["object_id"]]["mks"].append(members[id])
        elif descriptor["name"] == "knessets":
            for knesset in resource:
                knessets[knesset["KnessetNum"]] = []
                for id in knesset["faction"]:
                    knessets[knesset["KnessetNum"]].append(factions[id])

    for knesset_num, factions in knessets.items():
        build_template(jinja_env, "factions_index.html",
                       get_context({
                           "knesset_num": knesset_num,
                           "factions": factions,
                           "faction_url": FACTION_URL.format(knesset_num=knesset_num,faction_id="{faction_id}"),
                           "member_url": MEMBER_URL
                       }),
                       FACTION_HOME_URL.format(knesset_num=knesset_num))

        for faction in factions:
            build_template(jinja_env, "faction_detail.html",
                           get_context({
                               "knesset_num": knesset_num,
                               "faction_num": faction["faction_num"],
                               "faction_name": faction["faction_name"],
                               "mks": faction["mks"],
                               "faction_home_url": FACTION_HOME_URL.format(knesset_num=knesset_num),
                               "member_url": MEMBER_URL
                           }),
                           FACTION_URL.format(knesset_num=knesset_num,faction_id=faction["faction_num"]))

    if os.environ.get("SKIP_STATIC") != "1":
        subprocess.check_call(["mkdir", "-p", "dist"])
        subprocess.check_call(["cp", "-rf", "static", "dist/"])

    spew({}, [], {})


if __name__ == "__main__":
    main()
