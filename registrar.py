# Adapted from Penn Labs Code
# https://github.com/pennlabs/penn-courses/blob/master/backend/courses/registrar.py
import json
import logging
import requests
import secrets

logger = logging.getLogger(__name__)

API_URL = "https://3scale-public-prod-open-data.apps.k8s.upenn.edu/api"


def get_token():
    r = requests.post(
        secrets.OPEN_DATA_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(secrets.OPEN_DATA_CLIENT_ID, secrets.OPEN_DATA_OIDC_SECRET),
    )
    if not r.ok:
        raise ValueError(f"OpenData token URL responded with status code {r.status_code}: {r.text}")
    return r.json()["access_token"]


def get_headers():
    return {
        "Authorization": "Bearer " + get_token(),
    }


def make_api_request(params):
    headers = get_headers()
    url = f"{secrets.OPEN_DATA_API_BASE}/v1/course_section_search"
    r = requests.get(
        url,
        params=params,
        headers=headers,
    )
    if not r.ok:
        raise ValueError(f"OpenData API request failed with status code {r.status_code}: {r.text}")
    return r.json()


def report_api_error(err):
    try:
        msg = json.loads(err)
        logger.error(msg.get("service_meta", {}).get("error_text", "no error text"))
    except json.JSONDecodeError:
        logger.error("Penn API error", extra={"error_msg": err})


def get_all_course_status(semester):
    headers = get_headers()
    url = f"{secrets.OPEN_DATA_API_BASE}/v1/course_section_status/{semester}/all"
    r = requests.get(url, headers=headers)
    if r.status_code == requests.codes.ok:
        return r.json().get("result_data", [])
    else:
        report_api_error(r.text)
        raise RuntimeError(
            f"Registrar API request failed with code {r.status_code}. "
            f'Message returned: "{r.text}"'
        )


def get_course_status(semester, course):
    headers = get_headers()
    url = f"{secrets.OPEN_DATA_API_BASE}/v1/course_section_status/id/{semester}/{course}"
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
        "section_id": query,
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
    params = {"section_id": query, "term": semester}
    headers = get_headers()
    data, err = make_api_request(params, headers)
    if err is None and data is not None:
        return first(data["result_data"])
    else:
        report_api_error(err)
        return None
