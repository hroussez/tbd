from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.generate import generate_response

router = APIRouter()

# Define the request model
class GenerateRequest(BaseModel):
    prompt: str

@router.post("/gen")
async def generate_text(request: GenerateRequest):
    prompt = request.prompt
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    # Call the service layer to handle generation
    response = generate_response(prompt)
    return {"result": response}