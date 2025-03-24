from datetime import datetime
from enum import Enum
from typing import Dict, Optional

class PostStatus(Enum):
    """Enum for LinkedIn post status."""
    DRAFT = "draft"
    REVIEWED = "reviewed"
    PUBLISHED = "published"
    FAILED = "failed"


class LinkedInPost:
    """Model representing a LinkedIn post."""
    
    def __init__(
        self,
        video_id: str,
        content: str,
        title: Optional[str] = None,
        status: PostStatus = PostStatus.DRAFT,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        published_at: Optional[datetime] = None,
        reviewed_at: Optional[datetime] = None,
        reviewed_by: Optional[str] = None,
        published_url: Optional[str] = None,
        video_title: Optional[str] = None,
        video_url: Optional[str] = None
    ):
        self.video_id = video_id
        self.content = content
        self.title = title
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        self.published_at = published_at
        self.reviewed_at = reviewed_at
        self.reviewed_by = reviewed_by
        self.published_url = published_url
        self.video_title = video_title
        self.video_url = video_url
    
    def to_dict(self) -> Dict:
        """Convert LinkedInPost to dictionary for MongoDB storage."""
        return {
            "video_id": self.video_id,
            "content": self.content,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "published_at": self.published_at,
            "reviewed_at": self.reviewed_at,
            "reviewed_by": self.reviewed_by,
            "published_url": self.published_url,
            "video_title": self.video_title,
            "video_url": self.video_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LinkedInPost':
        """Create LinkedInPost from dictionary (from MongoDB)."""
        return cls(
            video_id=data["video_id"],
            content=data["content"],
            title=data.get("title"),
            status=PostStatus(data.get("status", "draft")),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            published_at=data.get("published_at"),
            reviewed_at=data.get("reviewed_at"),
            reviewed_by=data.get("reviewed_by"),
            published_url=data.get("published_url"),
            video_title=data.get("video_title"),
            video_url=data.get("video_url")
        )
    
    def mark_as_reviewed(self, reviewer: str = "admin") -> None:
        """Mark the post as reviewed."""
        self.status = PostStatus.REVIEWED
        self.reviewed_at = datetime.now()
        self.reviewed_by = reviewer
        self.updated_at = datetime.now()
    
    def mark_as_published(self, published_url: str) -> None:
        """Mark the post as published."""
        self.status = PostStatus.PUBLISHED
        self.published_at = datetime.now()
        self.published_url = published_url
        self.updated_at = datetime.now()
    
    def update_content(self, content: str, title: Optional[str] = None) -> None:
        """Update the post content."""
        self.content = content
        if title:
            self.title = title
        self.updated_at = datetime.now() 