from functools import wraps
from flask import redirect, session


def login_required(f):
    # decorator for html pages that require user to be logged in
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return wrapper


def logged_in():
    if session.get("user_id") is None:
        return False
    return True


def transform_post_rawData(Data):
    results_Data = Data["results"]
    url_results = []

    for element in results_Data:
        url_Data = element["urls"]
        url_results.append(url_Data["raw"])

    url_results.pop(9)

    return url_results


def transform_get_rawData(Data):
    url_results = []

    for element in Data:
        url_Data = element["urls"]
        url_results.append(url_Data["raw"])

    return url_results


def transform_login_rawData(Data):
    url_Data = Data["urls"]
    url_Data = url_Data["raw"]

    return url_Data


def send_email(user):
    import smtplib

    gmail_user = "the.official.blue.elephant@gmail.com"
    gmail_password = "developerPassw0rd"

    sent_from = gmail_user
    to = [user]
    subject = "Your Dose of Cuteness"
    body = "consectetur adipiscing elit"

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (
        sent_from,
        ", ".join(to),
        subject,
        body,
    )

    try:
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print("Email sent successfully!")
    except Exception as ex:
        print("Something went wrong….", ex)
