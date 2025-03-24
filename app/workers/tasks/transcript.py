import logging
from datetime import datetime
from typing import Dict, List, Optional

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

from app.workers.celery_app import app
from app.models.transcript import Transcript
from app.models.video import Video
from app.core.database import TranscriptRepository, VideoRepository

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3)
def extract_transcript(self, video_id: str) -> Optional[str]:
    """
    Extract transcript from a YouTube video.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Transcript ID if successful, None otherwise
    """
    logger.info(f"Extracting transcript for video ID: {video_id}")
    
    try:
        # Check if video exists in database
        video_data = VideoRepository.get_video(video_id)
        if not video_data:
            logger.error(f"Video not found in database: {video_id}")
            return None
        
        # Check if transcript already exists
        existing_transcript = TranscriptRepository.get_transcript(video_id)
        if existing_transcript:
            logger.info(f"Transcript already exists for video ID: {video_id}")
            return str(existing_transcript.get("_id"))
        
        # Get transcript from YouTube API
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(
                video_id, languages=['en']
            )
            
            # Create Transcript object
            transcript = Transcript.from_youtube_transcript_api(video_id, transcript_data)
            
            # Save transcript to database
            transcript_id = TranscriptRepository.save_transcript(transcript.to_dict())
            
            # Update video status
            video = Video.from_dict(video_data)
            video.processed = True
            video.processed_at = datetime.now()
            VideoRepository.save_video(video.to_dict())
            
            logger.info(f"Transcript extracted and saved for video ID: {video_id}")
            
            # Trigger summarization task
            from app.workers.tasks.summarize import generate_summary
            generate_summary.delay(video_id)
            
            return transcript_id
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.warning(f"No transcript available for video ID: {video_id}. Error: {str(e)}")
            
            # Update video status
            video = Video.from_dict(video_data)
            video.processed = True
            video.processed_at = datetime.now()
            VideoRepository.save_video(video.to_dict())
            
            return None
            
    except Exception as e:
        logger.error(f"Error extracting transcript for video ID: {video_id}. Error: {str(e)}")
        self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes
        return None 