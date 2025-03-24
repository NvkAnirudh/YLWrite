import logging
from typing import Dict, Optional

from openai import OpenAI

from app.workers.celery_app import app
from app.models.linkedin_post import LinkedInPost
from app.models.video import Video
from app.core.database import (
    VideoRepository, 
    SummaryRepository, 
    LinkedInPostRepository
)
from config.config import (
    AI_API_KEY, 
    AI_MODEL_NAME, 
    AI_MODEL_TYPE
)

logger = logging.getLogger(__name__)

# Initialize AI client
if AI_MODEL_TYPE == 'openai':
    ai_client = OpenAI(api_key=AI_API_KEY)

@app.task(bind=True, max_retries=3)
def generate_linkedin_post(self, video_id: str) -> Optional[str]:
    """
    Generate LinkedIn post draft from video summary.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        LinkedIn post ID if successful, None otherwise
    """
    logger.info(f"Generating LinkedIn post for video ID: {video_id}")
    
    try:
        # Check if video exists
        video_data = VideoRepository.get_video(video_id)
        if not video_data:
            logger.error(f"Video not found for video ID: {video_id}")
            return None
        
        # Check if summary exists
        summary_data = SummaryRepository.get_summary(video_id)
        if not summary_data:
            logger.warning(f"Summary not found for video ID: {video_id}")
            # We'll try to generate a post anyway, but it won't be as good
        
        # Check if post already exists
        existing_post = LinkedInPostRepository.get_post(video_id)
        if existing_post:
            logger.info(f"LinkedIn post already exists for video ID: {video_id}")
            
            # Trigger email notification
            from app.workers.tasks.email import send_post_notification
            send_post_notification.delay(video_id)
            
            return str(existing_post.get("_id"))
        
        # Create Video object
        video = Video.from_dict(video_data)
        
        # Generate LinkedIn post content
        post_content, post_title = _generate_linkedin_post_content(
            video_id=video_id,
            video_title=video.title,
            video_description=video.description or "",
            summary=summary_data.get("summary_text", "") if summary_data else "",
            key_points=summary_data.get("key_points", []) if summary_data else []
        )
        
        # Generate video URL
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Create LinkedIn post object
        linkedin_post = LinkedInPost(
            video_id=video_id,
            content=post_content,
            title=post_title,
            video_title=video.title,
            video_url=video_url
        )
        
        # Save LinkedIn post to database
        post_id = LinkedInPostRepository.save_post(linkedin_post.to_dict())
        
        logger.info(f"LinkedIn post generated and saved for video ID: {video_id}")
        
        # Trigger email notification
        from app.workers.tasks.email import send_post_notification
        send_post_notification.delay(video_id)
        
        return post_id
        
    except Exception as e:
        logger.error(f"Error generating LinkedIn post for video ID: {video_id}. Error: {str(e)}")
        self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes
        return None

def _generate_linkedin_post_content(
    video_id: str,
    video_title: str,
    video_description: str,
    summary: str,
    key_points: list
) -> tuple:
    """
    Generate LinkedIn post content using AI.
    
    Args:
        video_id: YouTube video ID
        video_title: Video title
        video_description: Video description
        summary: Video summary
        key_points: Key points from the video
        
    Returns:
        Tuple of (post_content, post_title)
    """
    if AI_MODEL_TYPE == 'openai':
        return _generate_openai_linkedin_post(
            video_id, video_title, video_description, summary, key_points
        )
    else:
        # Fallback to template-based generation
        return _generate_template_linkedin_post(
            video_id, video_title, video_description, summary, key_points
        )

def _generate_openai_linkedin_post(
    video_id: str,
    video_title: str,
    video_description: str,
    summary: str,
    key_points: list
) -> tuple:
    """
    Generate LinkedIn post content using OpenAI.
    
    Args:
        video_id: YouTube video ID
        video_title: Video title
        video_description: Video description
        summary: Video summary
        key_points: Key points from the video
        
    Returns:
        Tuple of (post_content, post_title)
    """
    # Combine available data
    key_points_text = "\n".join([f"- {point}" for point in key_points])
    
    # Prepare prompt
    prompt = f"""
    Create an informative, engaging, and professional LinkedIn post about a YouTube video I just watched.
    
    Video Title: {video_title}
    Video URL: https://www.youtube.com/watch?v={video_id}
    
    Video Summary: {summary}
    
    Key Points:
    {key_points_text}
    
    Additional Context:
    {video_description[:300]}
    
    Please create:
    1. A catchy title for my LinkedIn post (not more than 10 words)
    2. A professional but engaging LinkedIn post (around 200-250 words) that:
       - Hooks the reader with an interesting opening
       - Mentions the key insights from the video
       - Uses professional language suitable for LinkedIn
       - Includes 2-3 relevant hashtags at the end
       - Includes the video link
       - Has an engaging call-to-action
    
    Format your response with the Title on the first line, followed by the LinkedIn post content.
    """
    
    try:
        # Call OpenAI API
        response = ai_client.chat.completions.create(
            model=AI_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a professional social media content creator specializing in creating engaging LinkedIn posts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )
        
        # Parse response
        result = response.choices[0].message.content.strip()
        
        # Split into title and content
        lines = result.split("\n")
        post_title = lines[0].strip()
        if post_title.startswith("Title:"):
            post_title = post_title[6:].strip()
            
        # Rest is the post content
        post_content = "\n".join(lines[1:]).strip()
        if post_content.startswith("Post:"):
            post_content = post_content[5:].strip()
        
        # Ensure video URL is included
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        if video_url not in post_content:
            post_content += f"\n\n{video_url}"
        
        return post_content, post_title
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API for LinkedIn post: {str(e)}")
        return _generate_template_linkedin_post(
            video_id, video_title, video_description, summary, key_points
        )

def _generate_template_linkedin_post(
    video_id: str,
    video_title: str,
    video_description: str,
    summary: str,
    key_points: list
) -> tuple:
    """
    Generate LinkedIn post content using a template (fallback method).
    
    Args:
        video_id: YouTube video ID
        video_title: Video title
        video_description: Video description
        summary: Video summary
        key_points: Key points from the video
        
    Returns:
        Tuple of (post_content, post_title)
    """
    # Format key points as bullet points
    key_points_formatted = ""
    if key_points:
        key_points_formatted = "\n".join([f"• {point}" for point in key_points[:3]])
    
    # Generate post title
    post_title = f"Key Insights from: {video_title}"
    
    # Generate post content
    post_content = f"""
I just watched this insightful video: "{video_title}"

{summary[:150]}...

Top takeaways:
{key_points_formatted}

Check out the full video here: https://www.youtube.com/watch?v={video_id}

#ProfessionalDevelopment #ContinuousLearning #ContentSummary
    """.strip()
    
    return post_content, post_title 