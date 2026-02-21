from typing import Dict

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field

from service.feed_manager import RssAtomFeeds

router = APIRouter(prefix="/rssatom", tags=["feeds"])


class FeedRegistrationRequest(BaseModel):
    """
    Request payload for registering or deregistering a feed.
    """
    url: HttpUrl = Field(..., description="RSS/Atom feed URL")


class FeedActionResponse(BaseModel):
    """
    Standard API response for feed operations.
    """
    message: str
    url: HttpUrl


@router.post(
    "/register",
    response_model=FeedActionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_feed(request: FeedRegistrationRequest) -> FeedActionResponse:
    """
    Register and begin monitoring an RSS/Atom feed.

    Returns:
        FeedActionResponse: Confirmation of registration.
    """
    manager: RssAtomFeeds = RssAtomFeeds()

    try:
        await manager.register_feed(str(request.url))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    return FeedActionResponse(
        message="Feed registered successfully.",
        url=request.url,
    )


@router.post(
    "/deregister",
    response_model=FeedActionResponse,
    status_code=status.HTTP_200_OK,
)
async def deregister_feed(
        request: FeedRegistrationRequest,
) -> FeedActionResponse:
    """
    Stop monitoring an RSS/Atom feed.

    Returns:
        FeedActionResponse: Confirmation of deregistration.
    """
    manager: RssAtomFeeds = RssAtomFeeds()

    try:
        await manager.deregister_feed(str(request.url))

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    return FeedActionResponse(
        message="Feed deregistered successfully.",
        url=request.url,
    )
