import logging
from typing import Dict, List, Optional, Tuple

import openai
from openai import OpenAI

from app.workers.celery_app import app
from app.models.summary import Summary
from app.models.transcript import Transcript
from app.core.database import TranscriptRepository, SummaryRepository
from config.config import AI_API_KEY, AI_MODEL_NAME, AI_MODEL_TYPE

logger = logging.getLogger(__name__)

# Initialize AI client
if AI_MODEL_TYPE == 'openai':
    ai_client = OpenAI(api_key=AI_API_KEY)

@app.task(bind=True, max_retries=3)
def generate_summary(self, video_id: str) -> Optional[str]:
    """
    Generate summary of video transcript.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Summary ID if successful, None otherwise
    """
    logger.info(f"Generating summary for video ID: {video_id}")
    
    try:
        # Check if transcript exists
        transcript_data = TranscriptRepository.get_transcript(video_id)
        if not transcript_data:
            logger.error(f"Transcript not found for video ID: {video_id}")
            return None
        
        # Check if summary already exists
        existing_summary = SummaryRepository.get_summary(video_id)
        if existing_summary:
            logger.info(f"Summary already exists for video ID: {video_id}")
            
            # Trigger LinkedIn post generation
            from app.workers.tasks.linkedin_post import generate_linkedin_post
            generate_linkedin_post.delay(video_id)
            
            return str(existing_summary.get("_id"))
        
        # Create Transcript object from data
        transcript = Transcript.from_dict(transcript_data)
        
        # Generate summary using AI
        summary_text, key_points = _generate_ai_summary(transcript.get_full_text())
        
        # Create Summary object
        summary = Summary(
            video_id=video_id,
            summary_text=summary_text,
            key_points=key_points,
            model_used=AI_MODEL_NAME
        )
        
        # Save summary to database
        summary_id = SummaryRepository.save_summary(summary.to_dict())
        
        logger.info(f"Summary generated and saved for video ID: {video_id}")
        
        # Trigger LinkedIn post generation
        from app.workers.tasks.linkedin_post import generate_linkedin_post
        generate_linkedin_post.delay(video_id)
        
        return summary_id
        
    except Exception as e:
        logger.error(f"Error generating summary for video ID: {video_id}. Error: {str(e)}")
        self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes
        return None

def _generate_ai_summary(transcript_text: str) -> Tuple[str, List[str]]:
    """
    Generate summary and key points from transcript text using AI.
    
    Args:
        transcript_text: Full transcript text
        
    Returns:
        Tuple of (summary_text, key_points)
    """
    if AI_MODEL_TYPE == 'openai':
        return _generate_openai_summary(transcript_text)
    else:
        raise ValueError(f"Unsupported AI model type: {AI_MODEL_TYPE}")

def _generate_openai_summary(transcript_text: str) -> Tuple[str, List[str]]:
    """
    Generate summary using OpenAI API.
    
    Args:
        transcript_text: Full transcript text
        
    Returns:
        Tuple of (summary_text, key_points)
    """
    # Prepare prompt
    prompt = f"""
    Please analyze the following transcript from a YouTube video and provide:
    1. A concise summary (max 300 words) that captures the main points
    2. A list of 5-7 key points or takeaways from the video
    
    Transcript:
    {transcript_text[:4000]}  # Limit to 4000 chars to keep within token limits
    """
    
    try:
        # Call OpenAI API
        response = ai_client.chat.completions.create(
            model=AI_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes YouTube video transcripts concisely and extracts key points."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Parse response
        result = response.choices[0].message.content.strip()
        
        # Extract summary and key points
        parts = result.split("\n\n")
        
        summary_text = parts[0]
        if summary_text.startswith("Summary:"):
            summary_text = summary_text[8:].strip()
            
        # Extract key points
        key_points = []
        for part in parts[1:]:
            if "Key Points:" in part or "Takeaways:" in part:
                points_text = part.split(":", 1)[1].strip()
                points = [p.strip() for p in points_text.split("\n")]
                key_points = [p[2:].strip() if p.startswith("- ") else p for p in points if p]
                break
        
        # If key points weren't found in the expected format, try to parse them differently
        if not key_points:
            for part in parts[1:]:
                lines = part.split("\n")
                if len(lines) >= 3:  # At least 3 lines, likely bullet points
                    key_points = [line[2:].strip() if line.startswith("- ") else line.strip() for line in lines if line.strip()]
                    break
        
        # Ensure we have at least some key points
        if not key_points:
            key_points = ["No key points extracted"]
        
        return summary_text, key_points
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        return "Failed to generate summary due to AI service error.", ["Error processing transcript"] 