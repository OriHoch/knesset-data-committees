from tabulator import Stream
import os, requests, logging, re, json


def get_speech_part_body(speech_part):
    return speech_part["body"].replace("\n", "<br/>")


def get_speech_parts_stream(**kwargs):
    stream = Stream(**kwargs)
    stream.open()
    if stream.headers == ['header', 'body']:
        return stream
    else:
        return None


def get_speech_parts_source(meeting, parts_url):
    if os.environ.get("ENABLE_LOCAL_CACHING") == "1":
        parts_file = "data/minio-cache/committees/{}".format(meeting["parts_object_name"])
        if not os.path.exists(parts_file):
            os.makedirs(os.path.dirname(parts_file), exist_ok=True)
            with open(parts_file, "wb") as f:
                f.write(requests.get(parts_url).content)
        return "file", parts_file
    else:
        return "url", parts_url


def get_speech_part_contexts(stream):
    for order, row in enumerate(stream):
        if not row:
            header, body = "", ""
        elif len(row) == 2:
            header, body = row
        else:
            header, body = "", str(row)
        yield {"order": order,
               "header": header,
               "body": body}


def get_speech_parts(meeting):
    source_type, source = None, None
    if meeting["parts_object_name"]:
        parts_url = "https://minio.oknesset.org/committees/{}".format(meeting["parts_object_name"])
        try:
            source_type, source = get_speech_parts_source(meeting, parts_url)
            stream = get_speech_parts_stream(source=source, headers=1)
            if stream:
                yield from get_speech_part_contexts(stream)
                stream.close()
        except Exception:
            logging.exception("Failed to get speech parts for {}".format(meeting["parts_object_name"]))
            if source_type == "file" and os.path.exists(source):
                os.unlink(source)
            raise
