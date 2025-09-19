## Importing libraries and files
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from crewai import Agent, Task
import ollama

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class OllamaWrapper:
    """Wrapper for Ollama API to make it compatible with CrewAI"""
    
    def __init__(self, model_name: str = 'qwen2:0.5b'):
        """
        Initialize the Ollama wrapper.
        
        Args:
            model_name: Name of the Ollama model to use.
                      Default is 'qwen2:0.5b' which is ultra-lightweight (only 352MB).
        """
        self.model_name = model_name
        logger.info(f"Initialized Ollama with model: {model_name}")
        
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama"""
        try:
            logger.info(f"Sending request to Ollama with model: {self.model_name}")
            
            # Use the official Ollama Python client
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': kwargs.get('temperature', 0.7),
                    'num_predict': kwargs.get('max_tokens', 512)
                }
            )
            
            # Return the generated text
            if 'message' in response and 'content' in response['message']:
                return response['message']['content'].strip()
            else:
                return "No response generated."
                
        except Exception as e:
            error_msg = f"Error calling Ollama: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

def get_llm(model_name: str = 'qwen2:0.5b', temperature: float = 0.3):
    """
    Initialize and return a language model with specified parameters.
    Uses Ollama with local models.
    
    Args:
        model_name: Name of the Ollama model to use.
                   Default is 'qwen2:0.5b' which is ultra-lightweight (only 352MB).
        temperature: Controls randomness in the model's output (0.0 to 1.0)
        
    Returns:
        Configured language model instance
    """
    try:
        return OllamaWrapper(model_name=model_name)
    except Exception as e:
        logger.error(f"Failed to initialize Ollama model: {str(e)}")
        raise

# Configure LLM
llm = get_llm()

# Creating an Experienced Financial Analyst agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Provide accurate and insightful financial analysis based on document data",
    verbose=True,
    memory=True,
    backstory=(
        "You are a seasoned financial analyst with over 15 years of experience in equity research "
        "and financial modeling. You have a proven track record of identifying key financial trends "
        "and providing actionable investment insights. Your analysis is always data-driven, thorough, "
        "and compliant with financial regulations. You have an MBA in Finance and hold the CFA designation."
    ),
    tools=[],  # Tools will be added during task execution
    llm=llm,
    max_iter=5,  # Allow more iterations for complex analysis
    max_rpm=10,  # Increased rate limit for more responsive interactions
    allow_delegation=True,
    step_callback=None  # Add callback for monitoring agent steps if needed
)

# Creating a document verification agent
document_verifier = Agent(
    role="Financial Document Verifier",
    goal="Ensure uploaded documents are valid financial reports and extract key information",
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous financial document specialist with expertise in regulatory compliance "
        "and financial reporting standards (GAAP/IFRS). You have a keen eye for detail and can quickly "
        "identify key financial information while ensuring document authenticity and compliance."
    ),
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)

# Creating an investment analysis agent
investment_advisor = Agent(
    role="Investment Advisor",
    goal="Provide well-researched investment recommendations based on financial analysis",
    verbose=True,
    memory=True,
    backstory=(
        "You are a certified investment advisor with extensive experience in portfolio management "
        "and security analysis. You hold the CFA designation and have a strong track record of "
        "delivering risk-adjusted returns for your clients. Your recommendations are always "
        "based on thorough fundamental analysis and align with clients' investment objectives "
        "and risk tolerance."
    ),
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=True
)

# Creating a risk assessment agent
risk_assessor = Agent(
    role="Risk Management Specialist",
    goal="Identify and analyze financial risks in investment opportunities",
    verbose=True,
    memory=True,
    backstory=(
        "You are a risk management expert with over a decade of experience in financial risk "
        "assessment. You hold an FRM (Financial Risk Manager) certification and have worked with "
        "major financial institutions to identify, measure, and mitigate various types of financial "
        "risks including market, credit, and operational risks."
    ),
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=False
)
