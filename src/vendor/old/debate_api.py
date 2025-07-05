from fastapi import APIRouter

debate_router = APIRouter(prefix="/debate", tags=["debate"])


@debate_router.post("/rooms")
def create_debate_room():
    return {"success": True, "room_id": "mock_debate_room_id"}
