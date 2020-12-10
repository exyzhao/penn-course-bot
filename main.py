# Main script to check for courses repeatedly, and interact with
# Groupme API. Made by Brandon Wang, 2020.
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

    try:
        output = get_all_course_status("2021A", "all")  # hit all endpoints
        print("courses loaded")
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
            else:
                print(f"{current_time}: {entry_name} is closed!")
        # GroupMe messages
        if entry_name in groupme_alerts.keys():
            if entry['status'] == 'O':
                notif: str = f"{current_time}: {entry_name} is open!"
                print(notif)
                for p in groupme_alerts[entry_name]:
                    print(post_groupme_message(p, notif))
            else:
                print(f"{current_time}: {entry_name} is closed!")
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
    # Your Account Sid and Auth Token from twilio.com/console
    account_sid = Secrets.TWILIO_ACCOUNT_SID
    auth_token = Secrets.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=msg,
        from_='4154032721',  # hardcoded for now
        to=phone_num
    )

    return message.sid


if __name__ == '__main__':
    # Maps course id to phone num
    sms_alerts = {"CIS 120001": ["4699316958"]}
    # Maps course id to GroupMe group num
    groupme_alerts = {"CIS 121001": ["64423915"],
                      "CIS 262001": ["64440931"]}
    interval = 15.0  # Request interval, in seconds (should have 6000/hr cap)
    get_course_status()
