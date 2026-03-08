from fastapi import FastAPI
from routers import auth, users, tasks, recordings

app = FastAPI(title="SPG Evaluator")

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users Management"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks Management"])
app.include_router(recordings.router, prefix="/api/recordings", tags=["Recordings & NLP Scoring"])

@app.get("/")
async def root():
    return {"message": "API SPG Evaluator Berjalan Normal"}