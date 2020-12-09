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


def get_course_status():
    threading.Timer(interval, get_course_status).start()

    try:
        output = get_all_course_status("2021A", course)
        current_time = datetime.now().strftime("%H:%M:%S")

        if output[0]['status'] == 'O':
            notif: str = f"{current_time}: {course} is open!"
            print(notif)
            print(post_groupme_message(notif))
            # send_twilio_sms(target_num, notif) # disable for now?
        else:
            print(f"{current_time}: {course} is closed!")
        return 0
    except RuntimeError:
        raise SystemExit("Course Fetch had an error")


def post_groupme_message(msg: str):
    data = {
        "message": {
            "source_guid": str(round(time.time() * 1000)),
            "text": msg
        }
    }
    r = requests.post(GROUPME_URL,
                      data=json.dumps(data),
                      headers={'Content-Type': 'application/json'})

    if r.status_code == requests.codes.ok:
        return r.json(), None
    else:
        return None, r.text


def send_twilio_sms(phone_num: str, msg: str):
    # Your Account Sid and Auth Token from twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = Secrets.TWILIO_ACCOUNT_SID
    auth_token = Secrets.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body=msg,
        from_='4154032721',  # hardcoded for now
        to=phone_num
    )

    print(message.sid)


if __name__ == '__main__':
    course = "CIS 121001"
    group_id = "64423915"
    target_num = "4699316958" # sms destination
    interval = 10.0  # Request interval, in seconds (should have 6000/hr)
    GROUPME_URL = f"https://api.groupme.com/v3/groups/{group_id}/messages?token={Secrets.GM_TOKEN}"
    get_course_status()
