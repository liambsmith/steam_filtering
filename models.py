"""Data models for Steam games."""
from pydantic import BaseModel, Field
from typing import Optional, List


class SteamGame(BaseModel):
    """Represents a Steam game with match information."""
    
    # Match info
    original_title: str = Field(..., description="Title from CSV")
    steam_title: str = Field(..., description="Title from Steam")
    appid: int = Field(..., description="Steam AppID")
    url: str = Field(..., description="Steam store URL")
    
    # Match confidence
    match_score: float = Field(..., ge=0, le=100, description="Match confidence 0-100")
    is_exact_match: bool = Field(default=False, description="True if exact match")
    
    # Pricing (for reference)
    price: Optional[float] = Field(default=None, description="Price in USD")
    discount: Optional[int] = Field(default=None, description="Discount percentage")
    
    # Reviews
    positive_reviews: Optional[int] = Field(default=None, description="Number of positive reviews")
    negative_reviews: Optional[int] = Field(default=None, description="Number of negative reviews")
    review_score: Optional[int] = Field(default=None, ge=0, le=100, description="Review score 0-100")
    review_score_desc: Optional[str] = Field(default=None, description="Review description (e.g., 'Very Positive')")
    
    # Metadata
    released: Optional[str] = Field(default=None, description="Release date")
    top_tags: List[str] = Field(default_factory=list, description="Top user tags")
    genres: List[str] = Field(default_factory=list, description="Game genres")
    developer: Optional[str] = Field(default=None, description="Developer name")
    publisher: Optional[str] = Field(default=None, description="Publisher name")
    description: Optional[str] = Field(default=None, description="Short description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_title": "The Witcher 3",
                "steam_title": "The Witcher 3: Wild Hunt",
                "appid": 292030,
                "url": "https://store.steampowered.com/app/292030/",
                "match_score": 95.0,
                "is_exact_match": False,
                "price": 39.99,
                "discount": 0,
                "positive_reviews": 500000,
                "negative_reviews": 10000,
                "review_score": 97,
                "review_score_desc": "Overwhelmingly Positive",
                "released": "May 18, 2015",
                "top_tags": ["RPG", "Open World", "Story Rich", "Adventure", "Fantasy"],
                "genres": ["RPG", "Action"],
                "developer": "CD PROJEKT RED",
                "publisher": "CD PROJEKT RED",
                "description": "You are Geralt of Rivia..."
            }
        }
