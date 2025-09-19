import os
import logging
import asyncio
from celery import Celery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Analysis as AnalysisModel, AsyncSessionLocal, async_engine
from crewai import Crew, Process
from agents import financial_analyst, document_verifier, investment_advisor, risk_assessor, get_llm
from task import analyze_financial_document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_track_started=True,
)

async def process_analysis(analysis_id: str):
    """Async function to process the analysis."""
    async with AsyncSessionLocal() as db:
        try:
            # Get the analysis
            result = await db.execute(select(AnalysisModel).filter(AnalysisModel.id == analysis_id))
            analysis = result.scalars().first()
            
            if not analysis:
                logger.error(f"Analysis {analysis_id} not found.")
                return

            # Run the analysis
            financial_crew = Crew(
                agents=[financial_analyst, document_verifier, investment_advisor, risk_assessor],
                tasks=[analyze_financial_document],
                process=Process.hierarchical,
                manager_llm=get_llm(),
                verbose=True,
            )

            result = financial_crew.kickoff({
                'query': analysis.query,
                'file_path': analysis.file_path
            })

            # Update the analysis
            analysis.status = 'completed'
            analysis.result = result
            await db.commit()

        except Exception as e:
            logger.error(f"Error in Celery task for analysis {analysis_id}: {str(e)}", exc_info=True)
            await db.rollback()
            
            # Update with error status
            result = await db.execute(select(AnalysisModel).filter(AnalysisModel.id == analysis_id))
            analysis = result.scalars().first()
            if analysis:
                analysis.status = 'failed'
                analysis.error = str(e)
                await db.commit()
                
        finally:
            # Clean up the file
            result = await db.execute(select(AnalysisModel).filter(AnalysisModel.id == analysis_id))
            analysis = result.scalars().first()
            if analysis and analysis.file_path and os.path.exists(analysis.file_path):
                try:
                    os.remove(analysis.file_path)
                    logger.info(f"Cleaned up temporary file: {analysis.file_path}")
                except Exception as e:
                    logger.error(f"Error cleaning up file {analysis.file_path}: {str(e)}")

@celery_app.task(name="run_analysis_task")
def run_analysis_task(analysis_id: str):
    """
    Celery task to run the financial document analysis.
    This is the entry point for Celery.
    """
    # Run the async function in an event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_analysis(analysis_id))
