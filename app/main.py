from fastapi import FastAPI

from app.controller.movies import router as movies_router

app = FastAPI(
    title="Movie Rating System",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(movies_router)
