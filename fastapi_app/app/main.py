from fastapi import FastAPI
from app.api import endpoints

app = FastAPI()

# Include the router from the endpoints module
app.include_router(endpoints.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)