from fastapi import FastAPI

app = FastAPI()

# Import and include routers from other modules when they are created
# Example:
# from .api import router as api_router
# app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Todo API"}