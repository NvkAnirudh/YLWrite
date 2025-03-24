from datetime import datetime
from typing import Any, Dict, List, Optional
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from config.config import (
    MONGODB_URI,
    MONGODB_DB_NAME,
    MONGODB_COLLECTION_TRANSCRIPTS,
    MONGODB_COLLECTION_SUMMARIES,
    MONGODB_COLLECTION_POSTS
)

class MongoDB:
    """MongoDB database connection manager."""
    
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    
    @classmethod
    def get_client(cls) -> MongoClient:
        """Get MongoDB client instance."""
        if cls._client is None:
            cls._client = MongoClient(MONGODB_URI)
        return cls._client
    
    @classmethod
    def get_db(cls) -> Database:
        """Get MongoDB database instance."""
        if cls._db is None:
            cls._db = cls.get_client()[MONGODB_DB_NAME]
        return cls._db
    
    @classmethod
    def get_collection(cls, collection_name: str) -> Collection:
        """Get MongoDB collection."""
        return cls.get_db()[collection_name]
    
    @classmethod
    def get_videos_collection(cls) -> Collection:
        """Get videos collection."""
        return cls.get_collection("videos")
    
    @classmethod
    def get_transcripts_collection(cls) -> Collection:
        """Get transcripts collection."""
        return cls.get_collection(MONGODB_COLLECTION_TRANSCRIPTS)
    
    @classmethod
    def get_summaries_collection(cls) -> Collection:
        """Get summaries collection."""
        return cls.get_collection(MONGODB_COLLECTION_SUMMARIES)
    
    @classmethod
    def get_posts_collection(cls) -> Collection:
        """Get LinkedIn posts collection."""
        return cls.get_collection(MONGODB_COLLECTION_POSTS)
    
    @classmethod
    def close(cls) -> None:
        """Close MongoDB connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None

# Database repository implementation

class VideoRepository:
    """Repository for video data."""
    
    @staticmethod
    def save_video(video_data: Dict[str, Any]) -> str:
        """Save video to database."""
        collection = MongoDB.get_videos_collection()
        
        # Check if video already exists
        existing = collection.find_one({"video_id": video_data["video_id"]})
        if existing:
            # Update existing video
            collection.update_one(
                {"video_id": video_data["video_id"]},
                {"$set": video_data}
            )
            return str(existing["_id"])
        
        # Insert new video
        result = collection.insert_one(video_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_video(video_id: str) -> Optional[Dict[str, Any]]:
        """Get video by ID."""
        collection = MongoDB.get_videos_collection()
        return collection.find_one({"video_id": video_id})
    
    @staticmethod
    def list_videos(limit: int = 20, processed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """List videos with optional filtering."""
        collection = MongoDB.get_videos_collection()
        query = {}
        if processed is not None:
            query["processed"] = processed
        
        return list(collection.find(query).sort("published_at", pymongo.DESCENDING).limit(limit))


class TranscriptRepository:
    """Repository for transcript data."""
    
    @staticmethod
    def save_transcript(transcript_data: Dict[str, Any]) -> str:
        """Save transcript to database."""
        collection = MongoDB.get_transcripts_collection()
        
        # Check if transcript already exists
        existing = collection.find_one({"video_id": transcript_data["video_id"]})
        if existing:
            # Update existing transcript
            collection.update_one(
                {"video_id": transcript_data["video_id"]},
                {"$set": transcript_data}
            )
            return str(existing["_id"])
        
        # Insert new transcript
        result = collection.insert_one(transcript_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_transcript(video_id: str) -> Optional[Dict[str, Any]]:
        """Get transcript by video ID."""
        collection = MongoDB.get_transcripts_collection()
        return collection.find_one({"video_id": video_id})


class SummaryRepository:
    """Repository for summary data."""
    
    @staticmethod
    def save_summary(summary_data: Dict[str, Any]) -> str:
        """Save summary to database."""
        collection = MongoDB.get_summaries_collection()
        
        # Check if summary already exists
        existing = collection.find_one({"video_id": summary_data["video_id"]})
        if existing:
            # Update existing summary
            collection.update_one(
                {"video_id": summary_data["video_id"]},
                {"$set": summary_data}
            )
            return str(existing["_id"])
        
        # Insert new summary
        result = collection.insert_one(summary_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_summary(video_id: str) -> Optional[Dict[str, Any]]:
        """Get summary by video ID."""
        collection = MongoDB.get_summaries_collection()
        return collection.find_one({"video_id": video_id})


class LinkedInPostRepository:
    """Repository for LinkedIn post data."""
    
    @staticmethod
    def save_post(post_data: Dict[str, Any]) -> str:
        """Save LinkedIn post to database."""
        collection = MongoDB.get_posts_collection()
        
        # Check if post already exists
        existing = collection.find_one({"video_id": post_data["video_id"]})
        if existing:
            # Update existing post
            collection.update_one(
                {"video_id": post_data["video_id"]},
                {"$set": post_data}
            )
            return str(existing["_id"])
        
        # Insert new post
        result = collection.insert_one(post_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_post(video_id: str) -> Optional[Dict[str, Any]]:
        """Get LinkedIn post by video ID."""
        collection = MongoDB.get_posts_collection()
        return collection.find_one({"video_id": video_id})
    
    @staticmethod
    def list_posts(limit: int = 20, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List LinkedIn posts with optional filtering."""
        collection = MongoDB.get_posts_collection()
        query = {}
        if status:
            query["status"] = status
        
        return list(collection.find(query).sort("created_at", pymongo.DESCENDING).limit(limit))
    
    @staticmethod
    def update_post_status(video_id: str, status: str, **kwargs) -> bool:
        """Update LinkedIn post status."""
        collection = MongoDB.get_posts_collection()
        update_data = {"status": status, "updated_at": datetime.now(), **kwargs}
        
        result = collection.update_one(
            {"video_id": video_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0 