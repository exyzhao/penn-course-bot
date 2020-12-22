## PennInTouch Bot

This is a fully automated course registration bot for PennInTouch (think Penn Course Alert on steroids) written in Python. 

It queries the [OpenData REST API](https://esb.isc-seo.upenn.edu/8091/documentation/#coursestatusservice) to 
get course statuses every ~15 seconds (customizable). The user can input a list of courses to track.
Once a desired course is detected as open, it can send alerts through GroupMe and Twilio. 
Additionally, it can also automatically try to register for the course on PennInTouch using the Selenium browser framework.


## Setup
Optionally, first create a python virtual env.
Then run
```
pip install -r requirements.txt
```
Next, download a browser driver for Selenium. So far, only the Chrome driver is supported and tested. 
It can be found [here](https://chromedriver.chromium.org/downloads). Copy it to this project's root directory.


Next, you will need to create a secrets.py file in this directory to store authentication secrets. 
You do not have to provide credentials for features you are not using.
**Do not** commit this file to Github. 
A sample is provided below:
```
# Registrar API Keys (for OpenData access, request this from the link found on the OpenData page)
API_KEY = "UPENN_XX_XXXX_1234567"
API_SECRET = "abcasdhsakjdhasjd23123hkjas"
# GroupMe API Key (for sending GroupMe messages, get it from https://dev.groupme.com/)
GM_TOKEN = "abcasdhsakjdhasjd23123hkjas"
# Twilio auth (for sending SMS, get from twilio.com/console)
TWILIO_ACCOUNT_SID = "abcasdhsakjdhasjd23123hkjas"
TWILIO_AUTH_TOKEN = "abcasdhsakjdhasjd23123hkjas"
# Your PennKey (for automatic course registration)
PENNKEY = "mypennkey"
PENNKEY_PASS = "mypennkeypass"
```
Finally, to start the bot, run 
```
python main.py
```

## Misc 
This tool was inspired by:
- Penn Course Alert
- https://github.com/jondubin/PennCourseAutoBotRegister

This project is available with the MIT License. 