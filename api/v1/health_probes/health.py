"""
Api to check if the backend is running
"""
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/", status_code=200)
async def health_probe():
    """Health probe endpoint to check if the backend is running"""
    try:
        return {"detail": "all is well", "message": "Bolna AI Assesment Backend is running well"}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
