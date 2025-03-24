from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.database.connection import get_database_connection
from app.models.video import Video
from app.models.linkedin_post import LinkedInPost
from app.models.summary import VideoSummary
from datetime import datetime

ui_bp = Blueprint('ui', __name__)

# Add context processor for templates
@ui_bp.context_processor
def utility_processor():
    return dict(now=datetime.utcnow)

@ui_bp.route('/')
def index():
    db = get_database_connection()
    # Get the latest LinkedIn posts, limit to 20
    posts = list(db.linkedin_posts.find().sort("created_at", -1).limit(20))
    
    # Get the corresponding videos
    video_ids = [post['video_id'] for post in posts]
    videos = {video['video_id']: video for video in db.videos.find({"video_id": {"$in": video_ids}})}
    
    # Combine post data with video data
    combined_data = []
    for post in posts:
        if post['video_id'] in videos:
            combined_data.append({
                'post': post,
                'video': videos[post['video_id']]
            })
    
    return render_template('index.html', posts=combined_data)

@ui_bp.route('/post/<video_id>')
def view_post(video_id):
    db = get_database_connection()
    
    # Get video information
    video = db.videos.find_one({"video_id": video_id})
    if not video:
        flash("Video not found", "danger")
        return redirect(url_for('index'))
    
    # Get LinkedIn post
    post = db.linkedin_posts.find_one({"video_id": video_id})
    if not post:
        flash("LinkedIn post not found", "danger")
        return redirect(url_for('index'))
    
    # Get video summary if available
    summary = db.video_summaries.find_one({"video_id": video_id})
    
    return render_template('view_post.html', video=video, post=post, summary=summary)

@ui_bp.route('/post/<video_id>/edit', methods=['GET', 'POST'])
def edit_post(video_id):
    db = get_database_connection()
    
    # Get video information
    video = db.videos.find_one({"video_id": video_id})
    if not video:
        flash("Video not found", "danger")
        return redirect(url_for('index'))
    
    # Get LinkedIn post
    post = db.linkedin_posts.find_one({"video_id": video_id})
    if not post:
        flash("LinkedIn post not found", "danger")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Update post with form data
        updated_post = {
            "$set": {
                "title": request.form.get('title'),
                "content": request.form.get('content'),
                "status": "reviewed",
                "reviewed_at": datetime.utcnow()
            }
        }
        
        db.linkedin_posts.update_one({"video_id": video_id}, updated_post)
        flash("LinkedIn post updated successfully", "success")
        return redirect(url_for('view_post', video_id=video_id))
    
    return render_template('edit_post.html', video=video, post=post)

@ui_bp.route('/post/<video_id>/publish', methods=['POST'])
def publish_post(video_id):
    db = get_database_connection()
    
    # Get LinkedIn post
    post = db.linkedin_posts.find_one({"video_id": video_id})
    if not post:
        flash("LinkedIn post not found", "danger")
        return redirect(url_for('index'))
    
    # Check if post is in 'reviewed' status
    if post.get('status') != 'reviewed':
        flash("Post must be reviewed before publishing", "warning")
        return redirect(url_for('view_post', video_id=video_id))
    
    # Update post status to 'published'
    db.linkedin_posts.update_one(
        {"video_id": video_id},
        {"$set": {"status": "published", "published_at": datetime.utcnow()}}
    )
    
    # TODO: Implement actual LinkedIn API integration
    # This would be where you'd call the LinkedIn API to post
    
    flash("LinkedIn post has been marked as published", "success")
    return redirect(url_for('view_post', video_id=video_id)) 