from datapackage_pipelines.wrapper import ingest, spew
import logging

parameters, datapackage, resources = ingest()

for descriptor, resource in zip(datapackage["resources"], resources):
    descriptor["schema"] = {
        "fields": [
            {
                "name": "object_id",
                "type": "integer"
            },
            {
                "name": "object_type",
                "type": "string"
            },
            {
                "name": "object_name",
                "type": "string"
            },
            {
                "name": "knesset_num",
                "type": "integer"
            },
            {
                "name": "mk_individual_ids",
                "type": "array"
            }
        ],
        "primaryKey": ["object_id", "object_type"]
    }
    positions = {
        "position_id": {
            "type": "position",
            "name": "position"
        },
        "GovMinistryID": {
            "type": "ministry",
            "name": "GovMinistryName"
        },
        "FactionID": {
            "type": "faction",
            "name": "FactionName"
        },
        "CommitteeID": {
            "type": "committee",
            "name": "CommitteeName"
        }
    }
    data = {}

    for member in resource:
        id = member["mk_individual_id"]

        for rows in member["positions"]:
            for position, settings in positions.items():

                if(position in rows):
                    key = str(rows[position]) + settings["type"]

                    if(key in data):
                        if id not in data[key]["mk_individual_ids"]:
                            data[key]["mk_individual_ids"].append(id)
                    else:
                        data[key] = {
                            "object_id": rows[position],
                            "object_type": settings["type"],
                            "object_name": rows[settings["name"]],
                            "knesset_num": rows["KnessetNum"] if "KnessetNum" in rows else "",
                            "mk_individual_ids": [id]
                        }


def get_view_resource(data):
    for row in data.values():
        yield row


spew(dict(datapackage, resources=[descriptor]),
     [get_view_resource(data)])
