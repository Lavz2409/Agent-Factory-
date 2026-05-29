from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import todo_routes, auth_routes

# Initialize FastAPI app
app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routes
app.include_router(todo_routes.router, prefix="/todos", tags=["todos"])
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Todo App API"}