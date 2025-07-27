from airflow import DAG
from airflow.providers.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import os

default_args = {
    'owner': 'stock-news-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'stock_news_scheduler',
    default_args=default_args,
    description='Schedule news crawling and financial data fetching every 4 hours',
    schedule_interval=timedelta(hours=4),
    catchup=False,
    max_active_runs=1,
    tags=['stock-news', 'scheduler'],
)

# News Service Scheduler Task
news_scheduler_task = KubernetesPodOperator(
    task_id='news_service_scheduler',
    name='news-scheduler-pod',
    namespace='stock-news',
    image='news-service:latest',
    cmds=["python"],
    arguments=["scheduler_script.py"],
    env_vars={
        'NEWS_DATABASE_URL': os.getenv('NEWS_DATABASE_URL'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'RABBITMQ_URL': os.getenv('RABBITMQ_URL'),
    },
    secrets=[
        k8s.V1Secret(
            deploy_type='env',
            deploy_target='NEWS_DATABASE_URL',
            secret='db-secrets',
            key='news-db-url',
        ),
        k8s.V1Secret(
            deploy_type='env',
            deploy_target='GOOGLE_API_KEY',
            secret='api-secrets',
            key='gemini-api-key',
        ),
        k8s.V1Secret(
            deploy_type='env',
            deploy_target='RABBITMQ_URL',
            secret='queue-secrets',
            key='rabbitmq-url',
        ),
    ],
    resources={
        'request_memory': '512Mi',
        'request_cpu': '0.5',
        'limit_memory': '1Gi',
        'limit_cpu': '1.0',
    },
    is_delete_operator_pod=True,
    dag=dag,
)

# Company Service Scheduler Task
company_scheduler_task = KubernetesPodOperator(
    task_id='company_service_scheduler',
    name='company-scheduler-pod',
    namespace='stock-news',
    image='company-service:latest',
    cmds=["python"],
    arguments=["scheduler_script.py"],
    env_vars={
        'COMPANY_DATABASE_URL': os.getenv('COMPANY_DATABASE_URL'),
        'FMP_API_KEY': os.getenv('FMP_API_KEY'),
    },
    secrets=[
        k8s.V1Secret(
            deploy_type='env',
            deploy_target='COMPANY_DATABASE_URL',
            secret='db-secrets',
            key='company-db-url',
        ),
        k8s.V1Secret(
            deploy_type='env',
            deploy_target='FMP_API_KEY',
            secret='api-secrets',
            key='fmp-api-key',
        ),
    ],
    resources={
        'request_memory': '256Mi',
        'request_cpu': '0.25',
        'limit_memory': '512Mi',
        'limit_cpu': '0.5',
    },
    is_delete_operator_pod=True,
    dag=dag,
)

# Set task dependencies - có thể chạy parallel
news_scheduler_task
company_scheduler_task
