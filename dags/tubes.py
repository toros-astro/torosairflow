"""Example DAG showing how TOROS would operate under Apache Airflow."""

from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago

args = {
    "owner": "airflow",
}

dag = DAG(
    dag_id="routine_sky_survey",
    default_args=args,
    schedule_interval="0 0 * * *",
    start_date=days_ago(2),
    dagrun_timeout=timedelta(minutes=60),
    tags=["survey"],
)

load_night_bundle = BashOperator(
    task_id="load_night_bundle",
    bash_command="echo loading",
    dag=dag,
)

make_dark_master = BashOperator(
    task_id="make_dark_master",
    bash_command="echo dark",
    dag=dag,
)

make_flat_master = BashOperator(
    task_id="make_flat_master",
    bash_command="echo flat",
    dag=dag,
)

make_flatdark_correction = BashOperator(
    task_id="make_flatdark_correction",
    bash_command="echo flatdark",
    dag=dag,
)

load_night_bundle >> [make_dark_master, make_flat_master] >> make_flatdark_correction

if __name__ == "__main__":
    dag.cli()
