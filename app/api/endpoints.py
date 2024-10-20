import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, FastAPI, Form, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from twilio.twiml.messaging_response import MessagingResponse
from queue import Queue
import os
from starlette.responses import StreamingResponse

from app.services.prompt import generate_prompt

router = APIRouter()
prompt_queue: Queue = None
wav_queue: Queue = None

chat_history = [
    {"role": "user", "content": "let's go!"},
    {"role": "assistant", "content": "energetic nu-disco track with fast-paced beats, vibrant bass grooves, and funky synth melodies that make you want to dance"}
]

messages_history = []


def initialize_router(global_prompt_queue: Queue, global_wav_queue: Queue):
    global prompt_queue
    global wav_queue

    prompt_queue = global_prompt_queue
    wav_queue = global_wav_queue

    prompt = get_prompt_sync()  # Await the coroutine to get the result
    prompt_queue.put(prompt)
    prompt_queue.put(prompt)

@router.get("/stream")
async def stream():
    wav_file_path = wav_queue.get()
    prompt_queue.put(get_prompt_sync())

    if not os.path.exists(wav_file_path):
        raise HTTPException(status_code=404, detail="WAV file not found")

    def iterfile():
        with open(wav_file_path, "rb") as file_like:
            while True:
                chunk = file_like.read(8192)  # Read in 8KB chunks
                if not chunk:
                    break
                yield chunk

    # Create a streaming response from the generator
    response = StreamingResponse(iterfile(), media_type="audio/wav")
    
    # Add headers to suggest a filename for downloading, if necessary
    filename = os.path.basename(wav_file_path)
    response.headers["Content-Disposition"] = f"inline; filename={filename}"
    
    return response

@router.post("/prompt")
async def prompt(From: str = Form(...), Body: str = Form(...)):
    messages_history.append({"timestamp": datetime.now(), "content": Body, "from": From[-4:]})

    chat_history.append({"role": "user", "content": Body})
    latest_prompt = generate_prompt(chat_history)
    chat_history.append({"role": "assistant", "content": latest_prompt})

    response = MessagingResponse()
    response.message(latest_prompt)

    # return Response(content=str(response), media_type="application/xml")


@router.get("/prompt")
async def get_prompt():
    return chat_history[-1]["content"]


def get_prompt_sync():
    return chat_history[-1]["content"]

@router.get("/history")
async def history():
    return messages_history
