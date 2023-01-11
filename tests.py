from PITBot import PITBot


# def test_groupme():
#     """
#     Test the GroupMe send message function.
#     :return: server response
#     """
#     return bot.post_groupme_message("64440931", "this is a test")


def test_sms():
    """
    Test the Twilio SMS function
    :return: SID if message was sent correctly
    """
    return bot.send_twilio_sms("2147992608", "This is a test")


# def test_signup():
#     """
#     Tests course parsing and signup through Selenium.
#     :return: 0 if successful, 1 otherwise
#     """
#     return bot.signup("BEPP2500003")


# def test_load_all_courses():
#     """
#     Test loading courses
#     :return: dict as specified in the method docstring.
#     """
#     return bot.load_courses(semester="202310",
#                             get_all=True)


# def test_load_courses():
#     """
#     Test loading courses
#     :return: dict as specified in the method docstring.
#     """
#     return bot.load_courses(semester="202310",
#                             get_all=False,
#                             course_list=["CIS1600002", "OIDD2360001", "CIS1200203"])


if __name__ == '__main__':
    bot = PITBot({}, True, True, True)
    # print(test_load_all_courses())
    # print(test_load_courses())
    # print(test_groupme())
    print(test_sms())
    # print(test_signup())
