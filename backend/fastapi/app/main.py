from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .routers import health, auth, assessments, questions

settings = get_settings()

def create_app() -> FastAPI:
    app = FastAPI(
        title="SoulSense API",
        description="REST API for Soul Sense EQ Test - Assessments and Questions",
        version="1.0.0"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health.router, tags=["health"])
    app.include_router(auth.router, prefix="/auth", tags=["authentication"])
    app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["assessments"])
    app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])

    @app.on_event("startup")
    async def startup_event():
        app.state.settings = settings

    return app


app = create_app()
