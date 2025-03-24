import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Optional, List

from app.workers.celery_app import app
from app.models.video import Video
from app.models.linkedin_post import LinkedInPost
from app.core.database import VideoRepository, LinkedInPostRepository
from config.config import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_USE_TLS,
    EMAIL_RECIPIENT,
    WEB_UI_BASE_URL
)

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3)
def send_post_notification(self, video_id: str) -> bool:
    """
    Send notification email with LinkedIn post draft.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        True if email sent successfully, False otherwise
    """
    logger.info(f"Sending LinkedIn post notification for video ID: {video_id}")
    
    try:
        # Get video data
        video_data = VideoRepository.get_video(video_id)
        if not video_data:
            logger.error(f"Video not found for video ID: {video_id}")
            return False
        
        # Get LinkedIn post data
        post_data = LinkedInPostRepository.get_post(video_id)
        if not post_data:
            logger.error(f"LinkedIn post not found for video ID: {video_id}")
            return False
        
        # Create objects
        video = Video.from_dict(video_data)
        post = LinkedInPost.from_dict(post_data)
        
        # Send email
        result = _send_email(
            recipient=EMAIL_RECIPIENT,
            subject=f"LinkedIn Post Draft for: {video.title}",
            html_content=_generate_email_content(video, post)
        )
        
        if result:
            logger.info(f"LinkedIn post notification sent for video ID: {video_id}")
        else:
            logger.error(f"Failed to send LinkedIn post notification for video ID: {video_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending post notification for video ID: {video_id}. Error: {str(e)}")
        self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes
        return False

def _generate_email_content(video: Video, post: LinkedInPost) -> str:
    """
    Generate HTML email content.
    
    Args:
        video: Video object
        post: LinkedInPost object
        
    Returns:
        HTML email content
    """
    # Create edit link
    edit_link = f"{WEB_UI_BASE_URL}/posts/{video.video_id}/edit"
    
    # Generate HTML content
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #0077B5; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; border: 1px solid #ddd; border-radius: 0 0 5px 5px; }}
            .post-title {{ font-size: 22px; font-weight: bold; margin-bottom: 10px; color: #0077B5; }}
            .post-content {{ background-color: #f7f7f7; padding: 15px; border-radius: 5px; margin-bottom: 20px; white-space: pre-wrap; }}
            .video-details {{ margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #eee; }}
            .cta {{ background-color: #0077B5; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>LinkedIn Post Draft Ready for Review</h1>
        </div>
        <div class="content">
            <div class="video-details">
                <h2>Video Details</h2>
                <p><strong>Title:</strong> {video.title}</p>
                <p><strong>URL:</strong> <a href="https://www.youtube.com/watch?v={video.video_id}" target="_blank">https://www.youtube.com/watch?v={video.video_id}</a></p>
                <p><strong>Channel:</strong> {video.channel_title}</p>
                <p><strong>Published:</strong> {video.published_at.strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <h2>LinkedIn Post Draft</h2>
            <div class="post-title">{post.title or 'Untitled Post'}</div>
            <div class="post-content">{post.content}</div>
            
            <p>Please review and edit this draft before posting to LinkedIn.</p>
            <a href="{edit_link}" class="cta">Review & Edit Post</a>
            
            <div class="footer">
                <p>This email was sent automatically by your YouTube to LinkedIn pipeline.</p>
                <p>If you have any questions or issues, please contact your system administrator.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def _send_email(recipient: str, subject: str, html_content: str) -> bool:
    """
    Send email using SMTP.
    
    Args:
        recipient: Email recipient
        subject: Email subject
        html_content: HTML email content
        
    Returns:
        True if successful, False otherwise
    """
    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = recipient
    
    # Create HTML message
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    try:
        # Create SMTP server connection
        if EMAIL_USE_TLS:
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
        
        # Login to server
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Send email
        server.sendmail(EMAIL_HOST_USER, recipient, msg.as_string())
        
        # Close connection
        server.quit()
        
        logger.info(f"Email sent successfully to {recipient}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False 