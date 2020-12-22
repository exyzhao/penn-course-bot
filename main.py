"""
Main script to check for courses repeatedly, and interact with
Groupme API.
"""

from registrar import get_all_course_status
from autoregister import init_driver
import threading
from datetime import datetime
import time
import requests
import json
import secrets
from twilio.rest import Client
import autoregister


def get_course_status():
    """
    Grabs data from OpenData, and sends Twilio/Groupme alert messages.
    https://esb.isc-seo.upenn.edu/8091/documentation/#coursestatusservice
    :return: 0 if succeeded successfully
    """
    threading.Timer(interval, get_course_status).start()
    current_time = datetime.now().strftime("%H:%M:%S")

    try:
        output = []
        for course in sms_alerts.keys():
            output.append(get_all_course_status("2021A", course))  # hit all endpoints
        output = [item for sublist in output for item in sublist]
        print(f"{current_time}: courses loaded, length {len(output)}")
    except RuntimeError:
        raise SystemExit("Course Fetch had an error")

    current_time = datetime.now().strftime("%H:%M:%S")
    for entry in output:
        entry_name: str = entry['course_section']

        # get classes kek
        if entry_name in sms_alerts.keys():
            if entry['status'] == 'O':  # if course is open
                signup(entry_name)  # get class

        # Twilio SMS messages
        if entry_name in sms_alerts.keys():
            if entry['status'] == 'O':  # if course is open
                notif: str = f"{current_time}: {entry_name} is open!"
                print(notif)
                for p in sms_alerts[entry_name]:  # send alert to all phone nums
                    print(send_twilio_sms(p, notif))
            # else:
            #     print(f"{current_time}: {entry_name} is closed!")

        # GroupMe messages
        if entry_name in groupme_alerts.keys():
            if entry['status'] == 'O':
                notif: str = f"{current_time}: {entry_name} is open!"
                print(notif)
                for p in groupme_alerts[entry_name]:
                    print(post_groupme_message(p, notif))
            # else:
            #     print(f"{current_time}: {entry_name} is closed!")

    return 0


def post_groupme_message(group_id: str, msg: str):
    """
    Uses GroupMe API to send a message to a group via POST request.
    :param group_id: group id (share link)
    :param msg: any message string
    :return: server response
    """
    groupme_url = f"https://api.groupme.com/v3/groups/{group_id}/messages?token={secrets.gm_token}"
    data = {
        "message": {
            "source_guid": str(round(time.time() * 1000)),
            "text": msg
        }
    }
    r = requests.post(groupme_url,
                      data=json.dumps(data),
                      headers={'Content-Type': 'application/json'})

    if r.status_code == requests.codes.ok:
        return r.json(), None
    else:
        return None, r.text


def send_twilio_sms(phone_num: str, msg: str):
    """
    Sends Twilio message
    :param phone_num: user phone number
    :param msg: message string
    :return: confirmation that message was sent.
    """
    # if it's been less than 90 secs since last text to that #, do nothing
    if time.time() - last_sms[phone_num] < 90:
        return None
    else:
        message = client.messages.create(
            body=msg,
            from_='4155286397',  # hardcoded for now
            to=phone_num
        )
        last_sms[phone_num] = time.time()
        return message.sid


def signup(entry_name: str):
    """
    Signs up for course
    :param entry_name: unparsed course name
    :return: 0 if works, 1 if not
    """
    course_section = entry_name[-3:]
    course_number = entry_name[-6:-3]
    course_subject = entry_name[:-6].strip()
    chrome_driver = autoregister.init_driver()
    if autoregister.intouch_signup(chrome_driver, course_subject, course_number, course_section) == 0:
        return 0
    return 1


if __name__ == '__main__':
    # Launch Twilio Client
    client = Client(secrets.TWILIO_ACCOUNT_SID, secrets.TWILIO_AUTH_TOKEN)
    # Launch Web Driver
    chrome_driver = init_driver()
    auto_signup = False  # Flag to control automatic signups

    # Maps course id to phone num

    sms_alerts = {"BEPP250001": ["2482382012"],
                  "BEPP250002": ["2482382012"],
                  "ESE 301201": ["2482382012"],
                  "BEPP250003": ["2482382012"],
                  "EAS 203001": ["2482382012"],
                  "BEPP250006": ["2482382012"],
                  }
    # Maps course id to GroupMe group num
    groupme_alerts = {"BEPP250001": ["64456983"],
                      "BEPP250002": ["64456983"],
                      "ESE 301201": ["64456983"],
                      "BEPP250003": ["64456983"],
                      "EAS 203001": ["64456983"],
                      "BEPP250006": ["64456983"],
                      }

    interval = 15.0  # Request interval, in seconds (should have 6000/hr cap)
    # Track when we last sent a sms, for cooldown purposes
    last_sms = {phone: time.time() for phone in sum(sms_alerts.values(), [])}
    last_course = {course: time.time() for course in sms_alerts.keys()}
    get_course_status()
