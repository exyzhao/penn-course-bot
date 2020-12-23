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
        self.interval = 15.0  # Request interval, in seconds (current limit is 6000/hr)
        self.sms_alerts = sms_alerts
        self.groupme_alerts = groupme_alerts
        self.enable_signup = enable_signup
        self.enable_sms = enable_sms
        self.enable_groupme = enable_groupme
        self.last_sms = {phone: time.time() for phone in
                         sum(self.sms_alerts.values(), [])}  # Track when we last sent a sms, for cooldown purposes
        if self.enable_sms:
            self.client = Client(secrets.TWILIO_ACCOUNT_SID, secrets.TWILIO_AUTH_TOKEN)  # Launch Twilio Client
        if self.enable_signup:
            self.chrome_driver = autoregister.init_driver()  # Launch the web driver

    def start_bot(self):
        """
        Main function that the bot runs, repeated called using the threading Timer.
        """
        threading.Timer(self.interval, self.start_bot).start()  # Run every x seconds based on interval.
        course_status = self.load_courses(semester="2021A",
                                          get_all=False,
                                          course_list=list(self.sms_alerts.keys()))
        self.fire_alerts(course_status)

    def load_courses(self, semester, get_all=False, course_list=None):
        """
        Grabs data from OpenData, and sends Twilio/Groupme alert messages.
        https://esb.isc-seo.upenn.edu/8091/documentation/#coursestatusservice
        :return: dict of courses mapping course name to Open/Closed status
        """
        if course_list is None:
            course_list = []

        try:
            if get_all:
                output = get_all_course_status(semester, "all")
            else:
                output = [get_all_course_status(semester, course) for course in course_list]
                output = [item for sublist in output for item in sublist]  # Flatten list

            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"{current_time}: courses loaded, length {len(output)}")
            return {entry['course_section']: entry['status'] == 'O' for entry in output}
        except RuntimeError:
            raise SystemExit("Course Fetch had an error")

    def fire_alerts(self, course_status: dict):
        """
        Handles alerts for auto signup, SMS, and GroupMe
        :param course_status: dict of courses and their status.
        :return: None
        """
        for class_name, class_status in course_status.items():
            # Auto Signup for class if option is enabled and it's available
            if self.enable_signup and class_name in self.sms_alerts.keys() and class_status:
                self.signup(class_name)

            # Send Twilio SMS messages if enabled and it's available
            if self.enable_sms and class_name in self.sms_alerts.keys() and class_status:
                current_time = datetime.now().strftime("%H:%M:%S")
                notif = f"{current_time}: {class_name} is open!"
                print(notif)
                for phone_num in self.sms_alerts[class_name]:  # send alert to all phone nums
                    # if it's been less than 90 secs since last text to that #, do nothing
                    if time.time() - self.last_sms[phone_num] < 90:
                        return None
                    else:
                        print(self.send_twilio_sms(phone_num, notif))
                        self.last_sms[phone_num] = time.time()

            # Send GroupMe messages if enabled and it's available
            if self.enable_groupme and class_name in self.groupme_alerts.keys() and class_status:
                current_time = datetime.now().strftime("%H:%M:%S")
                notif = f"{current_time}: {class_name} is open!"
                print(notif)
                for p in self.groupme_alerts[class_name]:
                    print(self.post_groupme_message(p, notif))
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
