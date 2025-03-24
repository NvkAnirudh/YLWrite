import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'development-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', 't', '1')
    
    # MongoDB settings
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/youtube_tracker')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'youtube_tracker')
    
    # YouTube API settings
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID', '')
    
    # RabbitMQ settings
    RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
    
    # Email settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', 't', '1')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '') 