# Main script to check for courses repeatedly, and interact with
# Groupme API. Made by Brandon Wang, 2020.
# TODO: https://cloud.google.com/appengine/docs/standard/python3/quickstart?authuser=1
from registrar import get_all_course_status
import threading
from datetime import datetime
import time
import requests
import json
from secrets import Secrets
from twilio.rest import Client


# https://esb.isc-seo.upenn.edu/8091/documentation/#coursestatusservice
def get_course_status():
    threading.Timer(interval, get_course_status).start()
    current_time = datetime.now().strftime("%H:%M:%S")

    try:
        output = get_all_course_status("2021A", "all")  # hit all endpoints
        print(f"{current_time}: courses loaded, length {len(output)}")
    except RuntimeError:
        raise SystemExit("Course Fetch had an error")

    current_time = datetime.now().strftime("%H:%M:%S")
    for entry in output:
        entry_name: str = entry['course_section']
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
    groupme_url = f"https://api.groupme.com/v3/groups/{group_id}/messages?token={Secrets.GM_TOKEN}"
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
    # if it's been less than 60 secs since last text to that #, do nothing
    if time.time() - last_sms[phone_num] < 60:
        return None
    else:
        message = client.messages.create(
            body=msg,
            from_='4154032721',  # hardcoded for now
            to=phone_num
        )
        last_sms[phone_num] = time.time()
        return message.sid


if __name__ == '__main__':
    # Your Account Sid and Auth Token from twilio.com/console
    account_sid = Secrets.TWILIO_ACCOUNT_SID
    auth_token = Secrets.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    # Maps course id to phone num
    sms_alerts = {"EAS 203001": ["4699316958"],
                  "BEPP250001": ["4699316958"],
                  "BEPP250002": ["4699316958"],
                  "BEPP250003": ["4699316958"],
                  "BEPP250005": ["4699316958"],
                  "BEPP250006": ["4699316958"],
                  "BEPP250007": ["4699316958"],
                  "BEPP250008": ["4699316958"],
                  }
    # Maps course id to GroupMe group num
    groupme_alerts = {"EAS 203001": ["64423915"],
                      "BEPP250001": ["64423915"],
                      "BEPP250002": ["64423915"],
                      "BEPP250003": ["64423915"],
                      "BEPP250005": ["64423915"],
                      "BEPP250006": ["64423915"],
                      "BEPP250007": ["64423915"],
                      "BEPP250008": ["64423915"],
                      }
    interval = 15.0  # Request interval, in seconds (should have 6000/hr cap)
    # Track when we last sent a sms, for cooldown purposes
    last_sms = {phone: time.time() for phone in sum(sms_alerts.values(), [])}
    get_course_status()
