from PITBot import PITBot


def test_groupme():
    """
    Test the GroupMe send message function.
    :return: server response
    """
    return bot.post_groupme_message("64440931", "this is a test")


def test_sms():
    """
    Test the Twilio SMS function
    :return: SID if message was sent correctly
    """
    return bot.send_twilio_sms("4699316958", "this is a test")


def test_signup():
    """
    Tests course parsing and signup through Selenium.
    :return: 0 if successful, 1 otherwise
    """
    return bot.signup("BEPP250003")


if __name__ == '__main__':
    bot = PITBot({}, {}, True, True, True)
    print(test_groupme())
    print(test_sms())
    # print(test_signup())
