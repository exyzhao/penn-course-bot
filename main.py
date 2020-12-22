"""
Main script to check for courses repeatedly, and interact with
Groupme API.
"""
from PITBot import PITBot
from registrar import get_all_course_status
import threading
from datetime import datetime
import time
import autoregister


def start_bot():
    """
    Grabs data from OpenData, and sends Twilio/Groupme alert messages.
    https://esb.isc-seo.upenn.edu/8091/documentation/#coursestatusservice
    :return: 0 if succeeded successfully
    """
    current_time = datetime.now().strftime("%H:%M:%S")

    try:
        output = [get_all_course_status("2021A", course) for course in sms_alerts.keys()]
        output = [item for sublist in output for item in sublist]  # Flatten list
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
                for phone_num in sms_alerts[entry_name]:  # send alert to all phone nums
                    # if it's been less than 90 secs since last text to that #, do nothing
                    if time.time() - last_sms[phone_num] < 90:
                        return None
                    else:
                        print(send_twilio_sms(phone_num, notif))
                        last_sms[phone_num] = time.time()
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




if __name__ == '__main__':
    # Maps course id to phone num
    sms_alerts = {"BEPP250001": ["4699316958"],
                  "BEPP250002": ["4699316958"],
                  "ESE 301201": ["4699316958"],
                  "BEPP250003": ["4699316958"],
                  "EAS 203001": ["4699316958"],
                  "BEPP250006": ["4699316958"],
                  }
    # Maps course id to GroupMe group num
    groupme_alerts = {"BEPP250001": ["64440931"],
                      "BEPP250002": ["64440931"],
                      "ESE 301201": ["64440931"],
                      "BEPP250003": ["64440931"],
                      "EAS 203001": ["64440931"],
                      "BEPP250006": ["64440931"],
                      }

    bot = PITBot(sms_alerts, groupme_alerts, True, True, True)
