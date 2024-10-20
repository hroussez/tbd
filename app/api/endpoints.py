import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, FastAPI, Form, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from twilio.twiml.messaging_response import MessagingResponse

from app.services.stream import video_streamer
from app.services.prompt import generate_prompt

router = APIRouter()

chat_history = [
    {"role": "user", "content": "let's go!"},
    {"role": "assistant", "content": "energetic nu-disco track with fast-paced beats, vibrant bass grooves, and funky synth melodies that make you want to dance"}
]

messages_history = []

@router.get("/stream")
async def stream_video(token: str = Query(default=None)):
    try:
        video_streamer(token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

    # Create a streaming response from the generator
    response = StreamingResponse(video_streamer(token, get_prompt()), media_type="audio/wave")
    
    # Add headers to suggest a filename for downloading, if necessary
    response.headers["Content-Disposition"] = "inline; filename=audio.wav"
    
    # Include the new token in the response headers (optional, you can return it via JSON too)
    new_token = str(uuid.uuid4()) if token is None else token
    response.headers["X-New-Token"] = new_token
    
    return response

@router.post("/prompt")
async def prompt(From: str = Form(...), Body: str = Form(...)):
    messages_history.append({"timestamp": datetime.now(), "content": Body, "from": From[-4:]})

    chat_history.append({"role": "user", "content": Body})
    latest_prompt = generate_prompt(chat_history)
    chat_history.append({"role": "assistant", "content": latest_prompt})

    with open("prompt.txt", "w") as f:
        f.write(latest_prompt)

    response = MessagingResponse()
    response.message(latest_prompt)

    # return Response(content=str(response), media_type="application/xml")


@router.get("/prompt")
async def get_prompt():
    return chat_history[-1]["content"]

@router.get("/history")
async def history():
    return messages_history