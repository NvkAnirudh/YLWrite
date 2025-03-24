import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import googleapiclient.discovery
import pika

from app.models.video import Video
from app.core.database import VideoRepository
from config.config import (
    YOUTUBE_API_KEY,
    YOUTUBE_CHANNEL_ID,
    CHECK_INTERVAL_MINUTES,
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_VHOST,
    RABBITMQ_QUEUE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/youtube_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

class YouTubeMonitor:
    """Service for monitoring YouTube channel for new uploads."""
    
    def __init__(self):
        self.youtube = self._init_youtube_api()
        self.connection = None
        self.channel = None
        self._init_rabbitmq()
    
    def _init_youtube_api(self):
        """Initialize YouTube API client."""
        api_service_name = "youtube"
        api_version = "v3"
        
        logger.info("Initializing YouTube API client")
        return googleapiclient.discovery.build(
            api_service_name, 
            api_version, 
            developerKey=YOUTUBE_API_KEY
        )
    
    def _init_rabbitmq(self):
        """Initialize RabbitMQ connection."""
        logger.info("Connecting to RabbitMQ")
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host=RABBITMQ_VHOST,
            credentials=credentials
        )
        
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # Declare queue for video processing
        self.channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        logger.info(f"Connected to RabbitMQ and declared queue: {RABBITMQ_QUEUE}")
    
    def get_latest_videos(self, published_after: Optional[datetime] = None) -> List[Video]:
        """
        Get latest videos from channel.
        
        Args:
            published_after: Only return videos published after this datetime
            
        Returns:
            List of Video objects
        """
        request = self.youtube.search().list(
            part="snippet",
            channelId=YOUTUBE_CHANNEL_ID,
            maxResults=10,
            order="date",
            type="video"
        )
        
        response = request.execute()
        videos = []
        
        for item in response.get("items", []):
            # Create Video object from API response
            video = Video.from_youtube_api_response(item)
            
            # Check if video was published after the specified timestamp
            if published_after and video.published_at < published_after:
                continue
                
            videos.append(video)
        
        logger.info(f"Found {len(videos)} new videos")
        return videos
    
    def process_new_videos(self, videos: List[Video]) -> None:
        """
        Process list of new videos.
        
        For each video:
        1. Save to database
        2. Send message to RabbitMQ for processing
        """
        for video in videos:
            # Save video to database
            video_dict = video.to_dict()
            VideoRepository.save_video(video_dict)
            
            # Send message to RabbitMQ
            message = {
                "video_id": video.video_id,
                "title": video.title,
                "timestamp": datetime.now().isoformat()
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key=RABBITMQ_QUEUE,
                body=str(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            
            logger.info(f"Video queued for processing: {video.video_id} - {video.title}")
    
    def run(self) -> None:
        """Run the monitoring loop."""
        logger.info("Starting YouTube channel monitoring service")
        
        try:
            last_check_time = datetime.now() - timedelta(days=1)  # Start by checking last 24 hours
            
            while True:
                logger.info(f"Checking for new videos since {last_check_time}")
                
                # Get latest videos
                try:
                    videos = self.get_latest_videos(published_after=last_check_time)
                    
                    # Process new videos
                    if videos:
                        self.process_new_videos(videos)
                    
                except Exception as e:
                    logger.error(f"Error while checking YouTube API: {str(e)}")
                
                # Update last check time
                last_check_time = datetime.now()
                
                # Sleep until next check
                logger.info(f"Sleeping for {CHECK_INTERVAL_MINUTES} minutes until next check")
                time.sleep(CHECK_INTERVAL_MINUTES * 60)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down")
        finally:
            if self.connection:
                self.connection.close()
                logger.info("RabbitMQ connection closed")


if __name__ == "__main__":
    monitor = YouTubeMonitor()
    monitor.run() 