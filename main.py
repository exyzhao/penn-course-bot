"""
Main script to launch the bot.
"""
from PITBot import PITBot

if __name__ == '__main__':
    # Create a user
    brandon = {"groupme": "64440931",
               "sms": "4699316958"}
    # Create a user with no SMS
    user2 = {"groupme": "64423915",
             "sms": None}

    # Config mapping courses to a list of users
    alert_config = {"BEPP250003": [brandon, user2],
                    "EAS 203001": [brandon],
                    "CIS 160002": [brandon],
                    }

    # Create and launch the bot
    bot = PITBot(alert_config,
                 enable_signup=True,
                 enable_sms=False,
                 enable_groupme=False)
    bot.start_bot()
