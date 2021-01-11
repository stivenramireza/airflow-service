from airflow import DAG
from airflow.models import Variable
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator

from gym_booking.website_bot import (
    initialize,
    login_to_website,
    answer_questionnaire,
    search_headquarter,
    book_hour,
    get_qr_code,
    login_to_whatsapp,
    search_chat,
    send_message
)

from gym_booking.storage import (
    save_file,
    remove_file
)

from gym_booking.data_access_api import get_data

import os

default_args = {
    "owner": "stivenramireza",
    "email": ['stivenramireza@gmail.com'],
    "email_on_failure": True,
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
    "start_date": datetime(2021, 1, 10, 12, 5),
    "catchup_by_default": False,
    "provide_context": True
}

# Airflow Variables
dag_config = Variable.get("GYM_BOOKING_NATALY_VARIABLES", deserialize_json=True)
DRIVER_PATH = dag_config.get("DRIVER_PATH")
OUTPUT_PATH = dag_config.get("OUTPUT_PATH")
WEBSITE_URL = dag_config.get("WEBSITE_URL")
USERNAME = dag_config.get("USERNAME")
PASSWORD = dag_config.get("PASSWORD")
HEADQUARTER_NAME = dag_config.get("HEADQUARTER_NAME")
DESIRED_TIME = dag_config.get("DESIRED_TIME")
WHATSAPP_URL = dag_config.get("WHATSAPP_URL")
CHAT_NAME = dag_config.get("CHAT_NAME")
PERSON_NAME = dag_config.get("PERSON_NAME")
CHROME_PROFILE_PATH = dag_config.get("CHROME_PROFILE_PATH")

def dag_book_an_hour(**kwargs) -> None:
    driver = initialize(DRIVER_PATH, OUTPUT_PATH, CHROME_PROFILE_PATH)
    login_to_website(driver, WEBSITE_URL, USERNAME, PASSWORD)
    answer_questionnaire(driver)
    search_headquarter(driver, HEADQUARTER_NAME)
    book_hour(driver, DESIRED_TIME)
    qr_code_url = get_qr_code(driver)
    driver.close()
    return qr_code_url

def dag_download_qr_code(**kwargs) -> None:
    qr_code_url = kwargs["ti"].xcom_pull("book_an_hour")
    response = get_data(qr_code_url)
    image_path = os.path.join(OUTPUT_PATH, 'code.jpg')
    save_file(image_path, response)
    return image_path

def dag_send_whatsapp_message(**kwargs) -> None:
    image_path = kwargs["ti"].xcom_pull("download_qr_code")
    driver = initialize(DRIVER_PATH, OUTPUT_PATH, CHROME_PROFILE_PATH)
    login_to_whatsapp(driver, WHATSAPP_URL)
    search_chat(driver, CHAT_NAME)
    send_message(driver, image_path, PERSON_NAME, DESIRED_TIME)
    remove_file(image_path)
    driver.close()

with DAG(
        'gym_booking_nataly',
        default_args=default_args,
        description='Gym booking service DAG',
        schedule_interval='5 12 * * 1-5'
) as dag:

    book_an_hour = PythonOperator(
        task_id="book_an_hour", python_callable=dag_book_an_hour, provide_context=True
    )

    download_qr_code = PythonOperator(
        task_id="download_qr_code", python_callable=dag_download_qr_code, provide_context=True
    )

    send_whatsapp_message = PythonOperator(
        task_id="send_whatsapp_message", python_callable=dag_send_whatsapp_message, provide_context=True
    )

    book_an_hour >> download_qr_code >> send_whatsapp_message