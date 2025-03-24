from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.utils.dates import days_ago

import json
import requests
from bson.json_util import dumps, loads

# Define default arguments for DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'youtube_linkedin_pipeline',
    default_args=default_args,
    description='Process YouTube videos, generate transcripts, summaries, and LinkedIn posts',
    schedule_interval=None,  # Triggered externally
    start_date=days_ago(1),
    catchup=False,
    tags=['youtube', 'linkedin', 'content'],
)

# Define Python functions for each task

def process_new_video(**context):
    """
    Process new YouTube video from a trigger event.
    Extract video_id from the trigger payload.
    """
    # Get trigger data
    trigger_data = context['dag_run'].conf
    if not trigger_data or 'video_id' not in trigger_data:
        raise ValueError("No video_id provided in trigger data")
    
    video_id = trigger_data['video_id']
    print(f"Processing new video with ID: {video_id}")
    
    # Pass video_id to the next task
    context['ti'].xcom_push(key='video_id', value=video_id)
    return video_id

def extract_video_transcript(**context):
    """
    Extract transcript for the video.
    Calls the transcript extraction service.
    """
    # Get video_id from previous task
    video_id = context['ti'].xcom_pull(task_ids='process_new_video', key='video_id')
    
    # Call Celery task to extract transcript
    # In a production environment, you might use a direct API call or SDK
    # Here we're simulating a request to the worker service
    api_url = "http://webapp:8000/api/tasks/transcript"
    response = requests.post(
        api_url,
        json={"video_id": video_id}
    )
    
    if response.status_code != 200:
        print(f"Error extracting transcript: {response.text}")
        return None
    
    result = response.json()
    print(f"Transcript extraction initiated for video ID: {video_id}")
    return result

def generate_video_summary(**context):
    """
    Generate summary for the video transcript.
    """
    # Get video_id from first task
    video_id = context['ti'].xcom_pull(task_ids='process_new_video', key='video_id')
    
    # Call Celery task to generate summary
    api_url = "http://webapp:8000/api/tasks/summary"
    response = requests.post(
        api_url,
        json={"video_id": video_id}
    )
    
    if response.status_code != 200:
        print(f"Error generating summary: {response.text}")
        return None
    
    result = response.json()
    print(f"Summary generation initiated for video ID: {video_id}")
    return result

def create_linkedin_post(**context):
    """
    Create LinkedIn post draft from video summary.
    """
    # Get video_id from first task
    video_id = context['ti'].xcom_pull(task_ids='process_new_video', key='video_id')
    
    # Call Celery task to generate LinkedIn post
    api_url = "http://webapp:8000/api/tasks/linkedin-post"
    response = requests.post(
        api_url,
        json={"video_id": video_id}
    )
    
    if response.status_code != 200:
        print(f"Error creating LinkedIn post: {response.text}")
        return None
    
    result = response.json()
    print(f"LinkedIn post generation initiated for video ID: {video_id}")
    return result

def send_email_notification(**context):
    """
    Send email notification with LinkedIn post draft.
    """
    # Get video_id from first task
    video_id = context['ti'].xcom_pull(task_ids='process_new_video', key='video_id')
    
    # Call Celery task to send email notification
    api_url = "http://webapp:8000/api/tasks/email"
    response = requests.post(
        api_url,
        json={"video_id": video_id}
    )
    
    if response.status_code != 200:
        print(f"Error sending email notification: {response.text}")
        return None
    
    result = response.json()
    print(f"Email notification sent for video ID: {video_id}")
    return result

def update_status(**context):
    """
    Update processing status in MongoDB.
    """
    # Get video_id from first task
    video_id = context['ti'].xcom_pull(task_ids='process_new_video', key='video_id')
    
    # Connect to MongoDB using Airflow's MongoHook
    mongo_hook = MongoHook(conn_id='mongo_default')
    client = mongo_hook.get_conn()
    db = client.youtube_linkedin_pipeline
    
    # Update video status
    result = db.videos.update_one(
        {"video_id": video_id},
        {"$set": {
            "workflow_completed": True,
            "workflow_completed_at": datetime.now()
        }}
    )
    
    print(f"Updated workflow status for video ID: {video_id}")
    return {"updated": result.modified_count > 0}

# Define tasks
task_process_video = PythonOperator(
    task_id='process_new_video',
    python_callable=process_new_video,
    provide_context=True,
    dag=dag,
)

task_extract_transcript = PythonOperator(
    task_id='extract_video_transcript',
    python_callable=extract_video_transcript,
    provide_context=True,
    dag=dag,
)

task_generate_summary = PythonOperator(
    task_id='generate_video_summary',
    python_callable=generate_video_summary,
    provide_context=True,
    dag=dag,
)

task_create_linkedin_post = PythonOperator(
    task_id='create_linkedin_post',
    python_callable=create_linkedin_post,
    provide_context=True,
    dag=dag,
)

task_send_email = PythonOperator(
    task_id='send_email_notification',
    python_callable=send_email_notification,
    provide_context=True,
    dag=dag,
)

task_update_status = PythonOperator(
    task_id='update_status',
    python_callable=update_status,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
task_process_video >> task_extract_transcript >> task_generate_summary >> task_create_linkedin_post >> task_send_email >> task_update_status 