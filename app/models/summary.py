from datetime import datetime
from typing import Dict, List, Optional

class Summary:
    """Model representing a video summary."""
    
    def __init__(
        self,
        video_id: str,
        summary_text: str,
        key_points: List[str],
        created_at: Optional[datetime] = None,
        model_used: Optional[str] = None
    ):
        self.video_id = video_id
        self.summary_text = summary_text
        self.key_points = key_points
        self.created_at = created_at or datetime.now()
        self.model_used = model_used
    
    def to_dict(self) -> Dict:
        """Convert Summary to dictionary for MongoDB storage."""
        return {
            "video_id": self.video_id,
            "summary_text": self.summary_text,
            "key_points": self.key_points,
            "created_at": self.created_at,
            "model_used": self.model_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Summary':
        """Create Summary from dictionary (from MongoDB)."""
        return cls(
            video_id=data["video_id"],
            summary_text=data["summary_text"],
            key_points=data["key_points"],
            created_at=data["created_at"],
            model_used=data.get("model_used")
        ) 