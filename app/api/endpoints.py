from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

router = APIRouter()

# Define the request model
class GenerateRequest(BaseModel):
    prompt: str

@router.post("/gen")
async def generate_audio(request: GenerateRequest):
    prompt = request.prompt
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    # Define the path to the audio file
    audio_file_path = "data/sample_000.wav"
    
    # Check if the file exists
    if not os.path.exists(audio_file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Return the audio file
    return FileResponse(audio_file_path, media_type="audio/wav", filename="sample_000.wav")