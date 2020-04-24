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
    config_file='/home/airflow/docker_desktop_config', # where we stored our kubernetes config file
    cluster_context="tutorial-context", # our context
    in_cluster=False,


    namespace='tutorial-namespace', # our namespace
    image="redis_feeder:latest", # our local image
    name="redis-feeder-airflow", # our pod name
    image_pull_policy='Never', # to use local image
    arguments=["Defeated", "Sanity"], # some really cool arguments !

    env_vars={
        'ENVIRONMENT': 'production'
    },

    is_delete_operator_pod=True, # to delete the operator once done
    get_logs=True,
    dag=dag
)


dummy_operator >> kube_operator