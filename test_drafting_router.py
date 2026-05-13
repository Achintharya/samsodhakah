import uvicorn
from fastapi import FastAPI, APIRouter

# Create a simple test router
test_router = APIRouter(prefix="/test")

@test_router.get("/hello")
async def hello():
    return {"message": "Hello, World!"}

# Create a FastAPI app
app = FastAPI()

# Include the test router
app.include_router(test_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)