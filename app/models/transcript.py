from datetime import datetime
from typing import Dict, List, Optional

class TranscriptSegment:
    """Model representing a segment of a transcript."""
    
    def __init__(
        self,
        text: str,
        start: float,
        duration: float
    ):
        self.text = text
        self.start = start
        self.duration = duration
    
    def to_dict(self) -> Dict:
        """Convert TranscriptSegment to dictionary for MongoDB storage."""
        return {
            "text": self.text,
            "start": self.start,
            "duration": self.duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TranscriptSegment':
        """Create TranscriptSegment from dictionary (from MongoDB)."""
        return cls(
            text=data["text"],
            start=data["start"],
            duration=data["duration"]
        )


class Transcript:
    """Model representing a complete video transcript."""
    
    def __init__(
        self,
        video_id: str,
        segments: List[TranscriptSegment],
        language: str = "en",
        created_at: Optional[datetime] = None
    ):
        self.video_id = video_id
        self.segments = segments
        self.language = language
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert Transcript to dictionary for MongoDB storage."""
        return {
            "video_id": self.video_id,
            "segments": [segment.to_dict() for segment in self.segments],
            "language": self.language,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Transcript':
        """Create Transcript from dictionary (from MongoDB)."""
        return cls(
            video_id=data["video_id"],
            segments=[TranscriptSegment.from_dict(segment) for segment in data["segments"]],
            language=data["language"],
            created_at=data["created_at"]
        )
    
    @classmethod
    def from_youtube_transcript_api(cls, video_id: str, transcript_data: List[Dict]) -> 'Transcript':
        """Create Transcript from YouTube Transcript API response."""
        segments = [
            TranscriptSegment(
                text=item.get("text", ""),
                start=item.get("start", 0.0),
                duration=item.get("duration", 0.0)
            )
            for item in transcript_data
        ]
        
        return cls(
            video_id=video_id,
            segments=segments
        )
    
    def get_full_text(self) -> str:
        """Get the complete transcript text."""
        return " ".join(segment.text for segment in self.segments) 