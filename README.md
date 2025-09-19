# Financial Document Analyzer API

## Project Overview

A comprehensive financial document analysis system that processes corporate reports, financial statements, and investment documents using AI-powered agents. This system provides in-depth financial analysis, investment recommendations, and risk assessments through a robust FastAPI backend with Celery queue processing and database integration.

**🚀 Features:**
- **Local AI Processing**: Powered by Ollama for private, cost-free analysis
- **Multi-Agent System**: 4 specialized financial AI agents
- **Queue Processing**: Celery-based background task handling
- **Database Integration**: SQLAlchemy with async support
- **RESTful API**: FastAPI with automatic documentation
- **Production Ready**: CORS, error handling, logging, and more

---

## 🐛 Bugs Found and How We Fixed Them

### **Immediate Critical Issues Found:**

#### **a) agents.py Issues**
**Problems**:
- LLM not properly initialized (`llm = llm` was incorrect)
- Financial analyst agent had problematic goal and backstory
- Verifier agent was too permissive without proper document verification
- Investment advisor and risk assessor agents were not being utilized

**Solutions**:
- Fixed LLM initialization with proper Ollama integration
- Rewrote agent goals and backstories for professional financial analysis
- Enhanced document verification with strict validation rules
- Integrated all agents into the analysis workflow

#### **b) main.py Issues**
**Problems**:
- `run_crew` function didn't use the `file_path` parameter
- No error handling for invalid file types
- No validation of PDF content
- Missing proper API error responses

**Solutions**:
- Fixed file path handling in crew execution
- Added comprehensive file type validation
- Implemented PDF content verification
- Added proper HTTP status codes and error responses

#### **c) task.py Issues**
**Problems**:
- Tasks had unprofessional and non-compliant descriptions
- Expected outputs were not suitable for financial analysis
- Tasks didn't properly utilize the specialized agents

**Solutions**:
- Rewrote all task descriptions for professional financial analysis
- Defined clear, structured outputs for each analysis phase
- Properly mapped tasks to corresponding agent expertise

#### **d) tools.py Issues**
**Problems**:
- PDF class was not imported
- InvestmentTool and RiskTool were not properly implemented
- No error handling for file operations

**Solutions**:
- Added proper PDF parsing imports (`PyPDF2`)
- Fully implemented all financial analysis tools
- Added comprehensive error handling for file operations

#### **e) requirements.txt Issues**
**Problems**:
- Missing PDF parsing library
- Outdated package versions
- Missing essential dependencies

**Solutions**:
- Added `PyPDF2` and other missing libraries
- Updated all packages to compatible versions
- Added `ollama` for local AI processing

### **Security & Performance Issues Fixed:**

#### **Security Concerns Resolved**:
- **Input Validation**: Added comprehensive API endpoint validation
- **Path Traversal**: Secured file handling to prevent directory traversal
- **File Size Limits**: Implemented 10MB upload limit
- **Content Type Validation**: Strict PDF-only file acceptance

#### **Missing Features Implemented**:
- **Error Handling**: Comprehensive exception management
- **Logging**: Structured logging throughout the application
- **Response Formatting**: Consistent JSON API responses
- **Database Integration**: SQLAlchemy for persistent storage
- **Queue Processing**: Celery for background task handling

#### **Prompt Engineering Improvements**:
- **Structured Prompts**: Professional financial analysis instructions
- **Clear Hierarchy**: Defined agent roles and responsibilities
- **Context & Constraints**: Added proper analysis boundaries
- **Output Validation**: Ensured consistent, professional responses

### **Performance & Architecture Improvements:**
- **Local AI Processing**: Switched to Ollama for better performance and privacy
- **Async Processing**: Implemented Celery for background task handling
- **Database Integration**: Added SQLAlchemy models for persistent storage
- **Error Handling**: Comprehensive exception management throughout the application

---

## 🚀 Setup and Usage Instructions

### **Prerequisites**

- **Python 3.9+** 
- **Ollama** (for local AI models)
- **Redis** (optional, for Celery queue processing)
- **Git** (for cloning the repository)

### **Quick Start Installation**

#### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/financial-document-analyzer.git
cd financial-document-analyzer
```

#### **2. Set Up Python Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### **3. Install Ollama & AI Model**
```bash
# Install Ollama (Windows)
winget install ollama

# For macOS:
# brew install ollama

# For Linux:
# curl -fsSL https://ollama.ai/install.sh | sh

# Pull the lightweight model (352MB)
ollama pull qwen2:0.5b

# Verify installation
ollama --version
ollama list
```

#### **4. Install Python Dependencies**
```bash
pip install -r requirements.txt
```

#### **5. Configure Environment (Optional)**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys (optional for fallback)
# SERPAPI_API_KEY=your_serpapi_key_here
# GOOGLE_API_KEY=your_google_key_here
```

### **Running the Application**

#### **Option 1: Simple Mode (FastAPI Only)**
```bash
# Start the FastAPI server
uvicorn main:app --reload

# Access the API at: http://127.0.0.1:8000
# API Documentation: http://127.0.0.1:8000/docs
```

#### **Option 2: Full Mode (with Celery Queue Processing)**
```bash
# Terminal 1: Start Celery Worker
celery -A celery_worker.celery_app worker --pool=solo --loglevel=info

# Terminal 2: Start FastAPI Server
uvicorn main:app --reload
```

### **Testing the Installation**

#### **1. Health Check**
```bash
curl http://127.0.0.1:8000/
```

#### **2. Test Ollama Integration**
```bash
curl http://127.0.0.1:8000/test-ollama
```

#### **3. Upload and Analyze Document**
```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_financial_document.pdf" \
  -F "query=Analyze this company's financial performance"
```

### **Project Structure**
```
financial-document-analyzer/
├── agents.py              # AI agents with Ollama integration
├── celery_worker.py       # Background task processing (Bonus!)
├── database.py            # Database models & setup (Bonus!)
├── main.py               # FastAPI application
├── task.py               # Task definitions for agents
├── tools.py              # Financial analysis tools
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
└── data/                # Document upload directory
```

---

## API Documentation

The API provides three endpoints for managing financial document analysis.

#### `GET /`
*   **Description**: A health check endpoint to verify that the API is running.
*   **Response**: A JSON object indicating the status and version of the API.

#### `POST /analyze`
*   **Description**: Submits a financial document for analysis. This is an asynchronous endpoint that starts a background task.
*   **Form Data**:
    *   `file` (required): The financial document in PDF format.
    *   `query` (optional): A specific question or focus for the analysis (e.g., "What are the key risks for this company?").
*   **Response**: A JSON object confirming that the analysis has started, including a unique `analysis_id` to track the job.

#### `GET /analysis/{analysis_id}`
*   **Description**: Retrieves the status and results of an analysis task.
*   **Path Parameter**:
    *   `analysis_id` (required): The unique ID returned by the `/analyze` endpoint.
*   **Response**: A JSON object containing the status (`processing`, `completed`, or `failed`). If completed, the `analysis` field will contain the detailed report from the AI crew.

---

## 🎯 Bonus Features Implemented

### ✅ **Queue Worker Model** 
- **Celery Integration**: Background task processing with `celery_worker.py`
- **Async Processing**: Non-blocking document analysis
- **Concurrent Handling**: Multiple simultaneous analysis requests
- **Status Tracking**: Real-time progress monitoring

### ✅ **Database Integration**
- **SQLAlchemy Models**: Persistent storage with `database.py`
- **Async Database**: Non-blocking database operations
- **Analysis History**: Complete audit trail of all analyses
- **User Data Management**: Ready for multi-user scenarios

---

## 🏗️ Architecture

### **Multi-Agent AI System**
- **Senior Financial Analyst**: Deep financial statement analysis
- **Document Verifier**: PDF validation and data extraction  
- **Investment Advisor**: Investment recommendations and insights
- **Risk Management Specialist**: Comprehensive risk assessment

### **Technology Stack**
- **Backend**: FastAPI with async support
- **AI Processing**: Ollama with local qwen2:0.5b model
- **Queue System**: Celery for background processing
- **Database**: SQLAlchemy with async sessions
- **Document Processing**: PyPDF2 for text extraction

---

## 🚀 Deployment & Production

### **Docker Deployment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh
RUN ollama pull qwen2:0.5b

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Production Considerations**
- **Scalability**: Horizontal scaling with multiple Celery workers
- **Security**: API rate limiting and authentication
- **Monitoring**: Logging and performance metrics
- **Backup**: Database backup and disaster recovery

---

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Ollama**: Local AI model processing
- **CrewAI**: Multi-agent framework
- **FastAPI**: Modern web framework
- **Celery**: Distributed task queue
