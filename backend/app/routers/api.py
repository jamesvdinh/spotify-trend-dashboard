from fastapi import APIRouter, Depends

from ..deps import get_access_token
from ..spotify_client import get_current_user_profile

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/me")
async def me(access_token: str = Depends(get_access_token)):
    profile = await get_current_user_profile(access_token)
    return {
        "id": profile.get("id"),
        "display_name": profile.get("display_name"),
        "email": profile.get("email"),
        "product": profile.get("product"),
        "followers": profile.get("followers", {}).get("total"),
        "images": profile.get("images", []),
        "external_url": profile.get("external_urls", {}).get("spotify"),
        "country": profile.get("country"),
    }
