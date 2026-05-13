import uvicorn
from fastapi import FastAPI, APIRouter

# Create a simple test router
test_router = APIRouter(prefix="/api/drafting")

@test_router.get("/test")
async def test():
    return {"message": "Test endpoint works!"}

# Create a FastAPI app
app = FastAPI()

# Include the test router
app.include_router(test_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)