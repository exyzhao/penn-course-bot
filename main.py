"""
Main script to launch the bot.
"""
from PITBot import PITBot

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

    bot = PITBot(sms_alerts, groupme_alerts,
                 enable_signup=True,
                 enable_sms=True,
                 enable_groupme=True)
    bot.start_bot()
