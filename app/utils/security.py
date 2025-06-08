import os
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()
API_SECRET = os.getenv("API_SECRET", "")


def verify_api_key(x_api_key: str = Header(...)) -> None:
    """Validate provided API key from request headers."""
    if x_api_key != API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key",
        )
