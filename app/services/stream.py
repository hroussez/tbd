import os

def video_streamer(token: str, prompt: str):
    """Generator function to stream video content."""

    # Define the path to the video file
    video_file_path = f"data/sample_{token}.mp4"

    # Check if the file exists
    if not os.path.exists(video_file_path):
        raise Exception("Video file not found")

    with open(video_file_path, mode="rb") as video_file:
        while chunk := video_file.read(1024 * 1024):
            yield chunk
