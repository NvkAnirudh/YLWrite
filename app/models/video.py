from datetime import datetime
from typing import Dict, List, Optional

class Video:
    """Model representing a YouTube video."""
    
    def __init__(
        self,
        video_id: str,
        title: str,
        channel_id: str,
        channel_title: str,
        published_at: datetime,
        description: Optional[str] = None,
        thumbnail_url: Optional[str] = None
    ):
        self.video_id = video_id
        self.title = title
        self.channel_id = channel_id
        self.channel_title = channel_title
        self.published_at = published_at
        self.description = description
        self.thumbnail_url = thumbnail_url
        self.processed = False
        self.processed_at = None
    
    def to_dict(self) -> Dict:
        """Convert Video object to dictionary for MongoDB storage."""
        return {
            "video_id": self.video_id,
            "title": self.title,
            "channel_id": self.channel_id,
            "channel_title": self.channel_title,
            "published_at": self.published_at,
            "description": self.description,
            "thumbnail_url": self.thumbnail_url,
            "processed": self.processed,
            "processed_at": self.processed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Video':
        """Create Video object from dictionary (from MongoDB)."""
        video = cls(
            video_id=data["video_id"],
            title=data["title"],
            channel_id=data["channel_id"],
            channel_title=data["channel_title"],
            published_at=data["published_at"],
            description=data.get("description"),
            thumbnail_url=data.get("thumbnail_url")
        )
        video.processed = data.get("processed", False)
        video.processed_at = data.get("processed_at")
        return video
    
    @classmethod
    def from_youtube_api_response(cls, item: Dict) -> 'Video':
        """Create Video object from YouTube API response."""
        snippet = item.get("snippet", {})
        
        return cls(
            video_id=item.get("id", {}).get("videoId") if isinstance(item.get("id"), dict) else item.get("id"),
            title=snippet.get("title", ""),
            channel_id=snippet.get("channelId", ""),
            channel_title=snippet.get("channelTitle", ""),
            published_at=datetime.fromisoformat(snippet.get("publishedAt").replace("Z", "+00:00")) 
                         if snippet.get("publishedAt") else datetime.now(),
            description=snippet.get("description", ""),
            thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url", "")
        ) 