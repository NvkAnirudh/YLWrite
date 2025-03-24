# YLWrite (YouTube-to-LinkedIn Write)

An AI agent that monitors a specific YouTube channel for new uploads, extracts transcripts, summarizes content, and generates LinkedIn post drafts.

## System Components

1. **YouTube API Monitor**: Periodically checks for new videos on a specified YouTube channel
2. **RabbitMQ**: Message broker for task distribution
3. **Apache Airflow**: Workflow management for processing new videos
4. **Celery Workers**: Process tasks in the background
   - Video transcript extraction
   - Content summarization
   - LinkedIn post generation
5. **MongoDB**: Store video metadata, transcripts, summaries, and LinkedIn post drafts
6. **Web UI**: Review and modify LinkedIn post drafts
7. **Email Service**: Send notifications about new content

## Project Structure

```
Tracker/
├── app/
│   ├── __init__.py              # Flask app initialization 
│   ├── airflow/                 # Airflow DAGs (Directed Acyclic Graphs)
│   │   └── video_processing.py  # DAG for processing new videos
│   ├── celery_worker/           # Celery task configuration
│   │   ├── __init__.py
│   │   └── tasks.py             # Task definitions
│   ├── database/                # Database connection and utilities
│   │   ├── __init__.py
│   │   └── connection.py        # MongoDB connection utility
│   ├── email/                   # Email notification service
│   │   ├── __init__.py
│   │   └── notification.py      # Email notification functions
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── video.py             # Video model
│   │   ├── transcript.py        # Transcript model
│   │   ├── summary.py           # Summary model
│   │   └── linkedin_post.py     # LinkedIn post model
│   ├── ui/                      # Web UI
│   │   ├── __init__.py
│   │   ├── views.py             # Route handlers
│   │   └── templates/           # HTML templates
│   │       ├── base.html        # Base template
│   │       ├── index.html       # Home page
│   │       ├── view_post.html   # Post detail view
│   │       └── edit_post.html   # Post edit form
│   └── youtube/                 # YouTube API interaction
│       ├── __init__.py
│       └── api.py               # YouTube API functions
├── config.py                    # Configuration settings
├── run.py                       # Flask application entry point
├── Makefile                     # Automation commands
└── requirements.txt             # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB
- RabbitMQ
- Apache Airflow

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Tracker
   ```

2. Install dependencies:
   ```
   make install
   ```

3. Set up environment variables:
   Create a `.env` file in the project root with the following variables:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key
   YOUTUBE_CHANNEL_ID=target_channel_id
   MONGO_URI=mongodb://localhost:27017/
   MONGO_DB_NAME=youtube_tracker
   SECRET_KEY=your_flask_secret_key
   MAIL_USERNAME=your_email@example.com
   MAIL_PASSWORD=your_email_password
   NOTIFICATION_EMAIL=recipient@example.com
   ```

4. Initialize Airflow:
   ```
   make init-airflow
   ```

## Usage

### Running the Web UI

Start the Flask web interface:
```
make run-ui
```

The UI will be available at http://localhost:5000.

### Running the Celery Worker

Start the Celery worker for background task processing:
```
make run-worker
```

### Running Airflow

Start the Airflow webserver and scheduler:
```
make run-airflow
```

The Airflow dashboard will be available at http://localhost:8080.

## UI Functionality

The web interface provides the following functionality:

1. **Home Page**: Lists all LinkedIn post drafts generated from YouTube videos
2. **Post View**: Displays details about a LinkedIn post, including:
   - Video information (title, thumbnail, etc.)
   - Post status (draft, reviewed, published)
   - LinkedIn post content
   - Action buttons for editing and publishing
3. **Post Edit**: Allows editing of LinkedIn post content with:
   - Form for title and content
   - Auto-resize text area for better editing experience
   - Save functionality that updates the post status

## License

[MIT License](LICENSE) 
