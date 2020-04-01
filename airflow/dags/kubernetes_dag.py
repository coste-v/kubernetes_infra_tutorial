from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator


dag = DAG(
    'kube_dag', 
    description='Simple DAG to trigger a POD',
    schedule_interval='0 12 * * *',
    start_date=datetime(2017, 3, 20),
    catchup=False
)

dummy_operator = DummyOperator(task_id='dummy_task', retries=3, dag=dag)

kube_operator = KubernetesPodOperator(
    task_id='kube_task', 
    config_file='/home/airflow/docker_desktop_config',
    cluster_context="tutorial-context",
    in_cluster=False,


    namespace='tutorial-namespace',
    image="cron_code:latest",
    name="cron-code-test",
    image_pull_policy='Never',
    arguments=["Defeated", "Sanity"],

    env_vars={
        'ENVIRONMENT': 'production'
    },

    is_delete_operator_pod=True,
    get_logs=True,
    dag=dag
)


dummy_operator >> kube_operator