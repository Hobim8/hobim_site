from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, products 

app = FastAPI(
    title="Hobim Trades API",
    description="Backend services for Hobim Trades platform.",
    version="1.0.0",
)

# Configure CORS so the Next.js frontend can communicate with this API
app.add_middleware(
    CORSMiddleware,
    # TODO: Replace with specific frontend URL (e.g., https://hobimtrades.com) before production
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all modular routers here
app.include_router(auth.router)
app.include_router(products.router)


@app.get("/health", tags=["system"])
def health_check():
    """Simple health check endpoint for hosting platforms (Render/Railway)."""
    return {"status": "ok", "service": "Hobim Trades API"}