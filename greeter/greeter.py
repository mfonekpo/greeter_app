from prefect import flow, task
from prefect.tasks import task_input_hash
from prefect.logging import get_run_logger
import time
from dotenv import load_dotenv
load_dotenv()
import os
import keyring
import yagmail

email_id = os.getenv("EMAIL_ID")
password = os.getenv("PASSWORD")

fromaddress = email_id
toaddress = email_id
subject = "Greetings"

yag = yagmail.SMTP(
    fromaddress,
    os.getenv("EMAIL_PASSWORD")
)

@task(name="Get Time", log_prints=True)
def get_time():
    hour_of_day =time.localtime().tm_hour
    return hour_of_day

@task(name="Greet User", log_prints=True)
def greet_user(user, hour_of_day):
    if hour_of_day >=6 and hour_of_day < 12:
        return f"Good morning {user}"
    elif hour_of_day >= 12 and hour_of_day < 18:
        return f"Good afternoon {user}"
    elif hour_of_day >= 18 and hour_of_day < 24:
        return f"Good evening {user}"

@task(name="Send Email", log_prints=True, retries=3)
def send_email(user, hour_of_day):
    try:
        contents = greet_user(user, hour_of_day)
        yag.send(
            to=toaddress,
            subject=subject,
            contents=contents
        )
        print(f"Sending email from {fromaddress} to {toaddress} with subject {subject} and body {contents}")
    except Exception as e:
        print(f"Failed to send email: {e}")


@flow(name="Greet User", log_prints=True)
def main(user):
    hour_of_day = get_time()
    send_email(user, hour_of_day)


if __name__ == "__main__":
    main("Mfon Ekpo")