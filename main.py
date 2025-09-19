import os
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database import Base, Analysis as AnalysisModel, init_db, AsyncSessionLocal
from celery_worker import run_analysis_task

# Database session dependency
async def get_db():
    """Dependency to get a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial Document Analyzer API",
    description="API for analyzing financial documents using AI-powered agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_FILE_TYPES = ["application/pdf"]
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# --- Pydantic Models ---
class AnalysisResponse(BaseModel):
    """Response model for document analysis."""
    status: str
    analysis_id: Optional[str] = None
    message: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# --- Database Setup ---
@app.on_event("startup")
async def on_startup():
    """Initialize the database when the app starts."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")


# --- API Endpoints ---
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "success",
        "message": "Financial Document Analyzer API is running",
        "version": "1.0.0"
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(..., description="Financial document to analyze (PDF)"),
    query: str = Form(
        default="Analyze this financial document for investment insights",
        description="Specific query or focus for the analysis"
    )
):
    """
    Analyze a financial document and provide comprehensive investment recommendations.
    """
    try:
        if file.content_type not in SUPPORTED_FILE_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
        
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large.")
        
        analysis_id = str(uuid.uuid4())
        file_path = DATA_DIR / f"{analysis_id}.pdf"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        new_analysis = AnalysisModel(
            id=analysis_id,
            query=query.strip(),
            file_path=str(file_path),
            status='processing'
        )
        db.add(new_analysis)
        await db.commit()
        await db.refresh(new_analysis)
        
        # Dispatch the task to the Celery worker
        run_analysis_task.delay(analysis_id)
        
        return {
            "status": "processing",
            "analysis_id": analysis_id,
            "message": "Analysis started. Use the analysis_id to check the status."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get the status and results of a previously submitted analysis.
    """
    analysis = await db.get(AnalysisModel, analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    # Ensure we have the latest data
    await db.refresh(analysis)
    
    return {
        "status": analysis.status,
        "analysis_id": analysis.id,
        "analysis": analysis.result,
        "error": analysis.error,
        "message": "Analysis is still in progress." if analysis.status == 'processing' else None
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for consistent error responses."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "An unexpected error occurred.",
            "details": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)