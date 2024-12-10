from prefect import flow, task
from prefect.tasks import task_input_hash
from prefect.logging import get_run_logger
# from prefect_github.repository import GitHubRepository
import time
from dotenv import load_dotenv
load_dotenv()
import os
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
    logger = get_run_logger()
    hour_of_day = time.localtime().tm_hour
    logger.info(f"Current hour of the day: {hour_of_day}")
    return hour_of_day

@task(name="Greet User", log_prints=True)
def greet_user(user, hour_of_day):
    if hour_of_day >= 6 and hour_of_day < 12:
        return f"Good morning {user}"
    elif hour_of_day >= 12 and hour_of_day < 18:
        return f"Good afternoon {user}"
    elif hour_of_day >= 18 and hour_of_day < 24:
        return f"Good evening {user}"
    else:
        pass

@task(name="Send Email", log_prints=True, retries=3)
def send_email(user, hour_of_day):
    logger = get_run_logger()
    try:
        contents = greet_user(user, hour_of_day)
        yag.send(
            to=toaddress,
            subject=subject,
            contents=contents
        )
        logger.info(f"Sending email from {fromaddress} to {toaddress} with subject {subject} and body {contents}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

@flow(name="Greet User", log_prints=True)
def main(user: str="Mfon Ekpo"):
    logger = get_run_logger()
    logger.info(f"Flow started for user: {user}")
    hour_of_day = get_time()
    send_email(user, hour_of_day)


if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/mfonekpo/greeter_app.git",
        entrypoint="greeter.py:main",
    ).deploy(
        name="greeter_deployment",
        work_pool_name="modal-workpool",
        cron="*/2 * * * *",
        # timezone="Africa/Lagos"
    )
