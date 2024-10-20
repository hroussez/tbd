from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints
from queue import Queue
from app.core import audiocraft
import threading

app = FastAPI()

prompt_queue = Queue()
wav_queue = Queue()

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to allow specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

endpoints.initialize_router(prompt_queue, wav_queue)

# Include the router from the endpoints module
app.include_router(endpoints.router)

def process_queue():
    last_wav = None
    while True:
        prompt = prompt_queue.get()
        wav_file = audiocraft.generate_audio(prompt, last_wav)

        wav_queue.put(wav_file)

        last_wav = wav_file

if __name__ == "__main__":
    import uvicorn

    # Create and start the queue processing thread
    queue_thread = threading.Thread(target=process_queue, daemon=True)
    queue_thread.start()

    # Run the Uvicorn server
    uvicorn.run(app, host="127.0.0.1", port=8080)
