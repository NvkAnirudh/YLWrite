import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bootstrap import Bootstrap5
from datetime import datetime

from app.models.video import Video
from app.models.linkedin_post import LinkedInPost, PostStatus
from app.core.database import VideoRepository, LinkedInPostRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/webapp.log')
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Configure app
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'flatly'

# Initialize extensions
bootstrap = Bootstrap5(app)

# Routes

@app.route('/')
def index():
    """Landing page with list of posts."""
    # Get all posts, sorted by creation date
    posts = LinkedInPostRepository.list_posts(limit=50)
    
    # Get video details for each post
    for post in posts:
        video_data = VideoRepository.get_video(post['video_id'])
        if video_data:
            post['video_title'] = video_data.get('title', 'Unknown Video')
            post['video_thumbnail'] = video_data.get('thumbnail_url', '')
            post['channel_title'] = video_data.get('channel_title', 'Unknown Channel')
            post['published_at'] = video_data.get('published_at', datetime.now())
    
    return render_template('index.html', posts=posts)

@app.route('/posts/<video_id>/view')
def view_post(video_id):
    """View a LinkedIn post."""
    # Get post data
    post_data = LinkedInPostRepository.get_post(video_id)
    if not post_data:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))
    
    # Get video data
    video_data = VideoRepository.get_video(video_id)
    if not video_data:
        flash('Video not found', 'danger')
        return redirect(url_for('index'))
    
    # Create objects
    post = LinkedInPost.from_dict(post_data)
    video = Video.from_dict(video_data)
    
    return render_template('view_post.html', post=post, video=video)

@app.route('/posts/<video_id>/edit', methods=['GET', 'POST'])
def edit_post(video_id):
    """Edit a LinkedIn post."""
    # Get post data
    post_data = LinkedInPostRepository.get_post(video_id)
    if not post_data:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))
    
    # Get video data
    video_data = VideoRepository.get_video(video_id)
    if not video_data:
        flash('Video not found', 'danger')
        return redirect(url_for('index'))
    
    # Create objects
    post = LinkedInPost.from_dict(post_data)
    video = Video.from_dict(video_data)
    
    if request.method == 'POST':
        # Update post with form data
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        
        # Mark as reviewed
        post.mark_as_reviewed('admin')  # TODO: Use actual user ID
        
        # Save to database
        LinkedInPostRepository.save_post(post.to_dict())
        
        flash('Post updated successfully', 'success')
        return redirect(url_for('view_post', video_id=video_id))
    
    return render_template('edit_post.html', post=post, video=video)

@app.route('/posts/<video_id>/publish', methods=['POST'])
def publish_post(video_id):
    """Publish a LinkedIn post (mock implementation)."""
    # Get post data
    post_data = LinkedInPostRepository.get_post(video_id)
    if not post_data:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))
    
    # Create post object
    post = LinkedInPost.from_dict(post_data)
    
    # Check if post is reviewed
    if post.status != PostStatus.REVIEWED:
        flash('Post must be reviewed before publishing', 'warning')
        return redirect(url_for('view_post', video_id=video_id))
    
    # In a real implementation, this would call LinkedIn API
    # For now, we'll just mark as published with a mock URL
    post.mark_as_published(f"https://linkedin.com/post/{video_id}")
    
    # Save to database
    LinkedInPostRepository.save_post(post.to_dict())
    
    flash('Post published to LinkedIn', 'success')
    return redirect(url_for('view_post', video_id=video_id))

# API endpoints for Airflow/Celery integration

@app.route('/api/tasks/transcript', methods=['POST'])
def api_extract_transcript():
    """API endpoint to trigger transcript extraction."""
    data = request.json
    if not data or 'video_id' not in data:
        return jsonify({"error": "Missing video_id parameter"}), 400
    
    video_id = data['video_id']
    
    # In a real implementation, this would call the Celery task directly
    # For demo purposes, we'll just return a mock response
    return jsonify({
        "task_id": "mock-task-id",
        "video_id": video_id,
        "status": "started"
    })

@app.route('/api/tasks/summary', methods=['POST'])
def api_generate_summary():
    """API endpoint to trigger summary generation."""
    data = request.json
    if not data or 'video_id' not in data:
        return jsonify({"error": "Missing video_id parameter"}), 400
    
    video_id = data['video_id']
    
    # In a real implementation, this would call the Celery task directly
    # For demo purposes, we'll just return a mock response
    return jsonify({
        "task_id": "mock-task-id",
        "video_id": video_id,
        "status": "started"
    })

@app.route('/api/tasks/linkedin-post', methods=['POST'])
def api_generate_linkedin_post():
    """API endpoint to trigger LinkedIn post generation."""
    data = request.json
    if not data or 'video_id' not in data:
        return jsonify({"error": "Missing video_id parameter"}), 400
    
    video_id = data['video_id']
    
    # In a real implementation, this would call the Celery task directly
    # For demo purposes, we'll just return a mock response
    return jsonify({
        "task_id": "mock-task-id",
        "video_id": video_id,
        "status": "started"
    })

@app.route('/api/tasks/email', methods=['POST'])
def api_send_email():
    """API endpoint to trigger email notification."""
    data = request.json
    if not data or 'video_id' not in data:
        return jsonify({"error": "Missing video_id parameter"}), 400
    
    video_id = data['video_id']
    
    # In a real implementation, this would call the Celery task directly
    # For demo purposes, we'll just return a mock response
    return jsonify({
        "task_id": "mock-task-id",
        "video_id": video_id,
        "status": "started"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 