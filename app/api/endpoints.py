import uuid
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.stream import video_streamer

router = APIRouter()

prompt_history = []

@router.get("/stream")
async def stream_video(token: str = Query(default=None)):
    try:
        video_streamer(token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

    # Create a streaming response from the generator
    response = StreamingResponse(video_streamer(token, history), media_type="video/mp4")
    
    # Add headers to suggest a filename for downloading, if necessary
    response.headers["Content-Disposition"] = "inline; filename=video.mp4"
    
    # Include the new token in the response headers (optional, you can return it via JSON too)
    new_token = str(uuid.uuid4()) if token is None else token
    response.headers["X-New-Token"] = new_token
    
    return response

class PromptRequest(BaseModel):
    message: str

@router.post("/prompt")
async def prompt(request: PromptRequest):
    prompt_history.append(request.message)


@router.get("/history")
async def history():
    return prompt_history