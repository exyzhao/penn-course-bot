from registrar import get_all_course_status
import threading
from datetime import datetime
import time
import requests
import json
import secrets
from twilio.rest import Client
import autoregister


class PITBot:
    def __init__(self, sms_alerts: dict, groupme_alerts: dict, enable_signup=False, enable_sms=False,
                 enable_groupme=False):
        """
        Main Constructor.
        :param enable_signup: Whether to enable PIT signup automation
        :param enable_sms: Whether to enable SMS
        :param enable_groupme: Whether to enable Groupme
        :param sms_alerts: Dict of alerts for SMS (course to phone #)
        :param groupme_alerts: Dict of alerts for Groupme (course to group name)
        """
        self.client = Client(secrets.TWILIO_ACCOUNT_SID, secrets.TWILIO_AUTH_TOKEN)  # Launch Twilio Client
        self. chrome_driver = autoregister.init_driver()         # Launch the web driver
        self.interval = 15.0  # Request interval, in seconds (current limit is 6000/hr)
        self.last_sms = {phone: time.time() for phone in
                         sum(sms_alerts.values(), [])}  # Track when we last sent a sms, for cooldown purposes

    def start_bot(self):
        """
        Main function that the bot runs, repeated called using the threading Timer.
        :return:
        """
        threading.Timer(self.interval, self.start_bot).start()
        return 0

    def post_groupme_message(self, group_id: str, msg: str):
        """
        Uses GroupMe API to send a message to a group via POST request.
        :param group_id: group id (share link)
        :param msg: any message string
        :return: server response
        """
        groupme_url = f"https://api.groupme.com/v3/groups/{group_id}/messages?token={secrets.GM_TOKEN}"
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

    def send_twilio_sms(self, phone_num: str, msg: str):
        """
        Sends Twilio message
        :param phone_num: user phone number
        :param msg: message string
        :return: confirmation that message was sent.
        """
        message = self.client.messages.create(
            body=msg,
            from_=secrets.TWILIO_PHONE,  # hardcoded for now
            to=phone_num
        )
        return message.sid

    def signup(self, entry_name: str):
        """
        Signs up for course
        :param entry_name: unparsed course name to register. Should be in the form DEPT######.
        :return: 0 if successful, 1 otherwise
        """
        # Returns if the entry name is invalid
        if not len(entry_name) == 10:
            return 1
        course_section = entry_name[-3:]
        course_number = entry_name[-6:-3]
        course_subject = entry_name[:-6].strip()
        # Try to register for the course
        return 0 if autoregister.intouch_signup(self.chrome_driver, course_subject, course_number,
                                                course_section) == 0 else 1
