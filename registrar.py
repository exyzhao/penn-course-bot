# Adapted from Penn Labs Code
# https://github.com/pennlabs/penn-courses/blob/master/backend/courses/registrar.py
import json
import logging
import requests
from secrets import Secrets

logger = logging.getLogger(__name__)

API_URL = "https://esb.isc-seo.upenn.edu/8091/open_data/course_section_search"


def get_headers():
    """This will have a rotation of API keys eventually"""
    return {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization-Bearer": Secrets.API_KEY,
        "Authorization-Token": Secrets.API_SECRET
    }


def make_api_request(params, headers):
    if headers is None:
        headers = get_headers()

    r = requests.get(API_URL, params=params, headers=headers)

    if r.status_code == requests.codes.ok:
        return r.json(), None
    else:
        return None, r.text


def report_api_error(err):
    try:
        msg = json.loads(err)
        logger.error(msg.get("service_meta", {}).get("error_text", "no error text"))
    except json.JSONDecodeError:
        logger.error("Penn API error", extra={"error_msg": err})


def get_all_course_status(semester: str, course: str):
    headers = get_headers()
    url = f"https://esb.isc-seo.upenn.edu/8091/open_data/course_status/{semester}/{course}"
    r = requests.get(url, headers=headers)
    if r.status_code == requests.codes.ok:
        return r.json().get("result_data", [])
    else:
        report_api_error(r.text)
        raise RuntimeError(
            f"Registrar API request failed with code {r.status_code}. "
            f'Message returned: "{r.text}"'
        )


def get_courses(query, semester):
    headers = get_headers()

    params = {
        "course_id": query,
        "term": semester,
        "page_number": 1,
        "number_of_results_per_page": 200,
    }

    results = []
    while True:
        logger.info("making request for page #%d" % params["page_number"])
        data, err = make_api_request(params, headers)
        if data is not None:
            next_page = data["service_meta"]["next_page_number"]
            results.extend(data["result_data"])
            if int(next_page) <= params["page_number"]:
                break
            params["page_number"] = next_page
        else:
            report_api_error(err)
            break

    return results


def first(lst):
    if len(lst) > 0:
        return lst[0]


def get_course(query, semester):
    params = {"course_id": query, "term": semester}
    headers = get_headers()
    data, err = make_api_request(params, headers)
    if err is None and data is not None:
        return first(data["result_data"])
    else:
        report_api_error(err)
        return None
