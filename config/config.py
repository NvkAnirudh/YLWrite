import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# YouTube API Configuration
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
YOUTUBE_CHANNEL_ID = os.environ.get('YOUTUBE_CHANNEL_ID')
CHECK_INTERVAL_MINUTES = int(os.environ.get('CHECK_INTERVAL_MINUTES', 60))

# MongoDB Configuration
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'youtube_linkedin_pipeline')
MONGODB_COLLECTION_TRANSCRIPTS = 'transcripts'
MONGODB_COLLECTION_SUMMARIES = 'summaries'
MONGODB_COLLECTION_POSTS = 'linkedin_posts'

# RabbitMQ Configuration
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST', '/')
RABBITMQ_QUEUE = os.environ.get('RABBITMQ_QUEUE', 'youtube_new_videos')

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', f'mongodb://{MONGODB_URI}/{MONGODB_DB_NAME}')

# Email Configuration
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_RECIPIENT = os.environ.get('EMAIL_RECIPIENT')

# Web UI Configuration
WEB_UI_HOST = os.environ.get('WEB_UI_HOST', '0.0.0.0')
WEB_UI_PORT = int(os.environ.get('WEB_UI_PORT', 8000))
WEB_UI_BASE_URL = os.environ.get('WEB_UI_BASE_URL', f'http://localhost:{WEB_UI_PORT}')

# LinkedIn API Configuration
LINKEDIN_CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET')
LINKEDIN_REDIRECT_URI = os.environ.get('LINKEDIN_REDIRECT_URI', f'{WEB_UI_BASE_URL}/auth/linkedin/callback')

# AI Configuration for Summarization and Post Generation
AI_MODEL_TYPE = os.environ.get('AI_MODEL_TYPE', 'openai')  # or 'huggingface', etc.
AI_API_KEY = os.environ.get('AI_API_KEY')
AI_MODEL_NAME = os.environ.get('AI_MODEL_NAME', 'gpt-4') 