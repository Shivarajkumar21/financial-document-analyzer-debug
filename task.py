## Importing libraries and files
from typing import Dict, Any, List
from crewai import Task
from agents import financial_analyst, document_verifier, investment_advisor, risk_assessor
from tools import FinancialDocumentTool, InvestmentAnalysisTool, RiskAssessmentTool
from crewai.tools.base_tool import Tool

# Create tool instances from the methods
read_document_tool = Tool(
    name="Read Financial Document",
    description="Reads and processes text from a PDF financial document, given a file path.",
    func=FinancialDocumentTool.read_data_tool
)

analyze_investment_tool = Tool(
    name="Analyze Investment Potential",
    description="Analyzes investment opportunities from the text of a financial document.",
    func=InvestmentAnalysisTool.analyze_investment
)

assess_risk_tool = Tool(
    name="Assess Financial Risk",
    description="Assesses financial risks from the text of a financial document.",
    func=RiskAssessmentTool.assess_risk
)

# Document Verification Task
document_verification_task = Task(
    description=(
        "Carefully review the uploaded financial document to verify its authenticity "
        "and extract key information. The document path is: {file_path}.\n\n"
        "1. Verify if the document appears to be a legitimate financial report\n"
        "2. Identify the company name, reporting period, and document type\n"
        "3. Extract key financial metrics (revenue, net income, EPS, etc.)\n"
        "4. Note any red flags or inconsistencies in the document\n"
        "5. Prepare a summary of the document's key contents\n\n"
        "Be thorough and precise in your analysis, as this will inform subsequent tasks."
    ),
    expected_output=(
        "A structured report containing:\n"
        "1. Document verification status (Verified/Suspicious/Unverified)\n"
        "2. Company identification and reporting period\n"
        "3. Key financial metrics extracted from the document\n"
        "4. Any notable findings or concerns about the document\n"
        "5. A brief summary of the document's contents"
    ),
    agent=document_verifier,
    tools=[read_document_tool],
    async_execution=True,
    context=[]
)

# Financial Analysis Task
financial_analysis_task = Task(
    description=(
        "Conduct a comprehensive analysis of the financial document located at {file_path}. "
        "The user's specific query is: {query}\n\n"
        "Your analysis should include:\n"
        "1. Company overview and business model analysis\n"
        "2. Financial performance review (revenue growth, profitability, etc.)\n"
        "3. Key financial ratios and their implications\n"
        "4. Cash flow analysis and capital structure\n"
        "5. Any significant trends or anomalies in the financial data\n\n"
        "Provide clear, data-driven insights with references to specific figures from the document."
    ),
    expected_output=(
        "A detailed financial analysis report containing:\n"
        "1. Executive summary of key findings\n"
        "2. Financial performance metrics and analysis\n"
        "3. Ratio analysis with industry comparisons\n"
        "4. Cash flow and liquidity assessment\n"
        "5. Conclusion and key takeaways"
    ),
    agent=financial_analyst,
    tools=[read_document_tool],
    async_execution=True,
    context=[document_verification_task]
)

# Investment Analysis Task
investment_analysis_task = Task(
    description=(
        "Based on the financial analysis of the document at {file_path}, provide "
        "investment recommendations. The user's specific query is: {query}\n\n"
        "Consider the following in your analysis:\n"
        "1. Company valuation relative to industry peers\n"
        "2. Growth prospects and competitive advantages\n"
        "3. Financial health and sustainability metrics\n"
        "4. Potential risks and mitigating factors\n"
        "5. Current market conditions and industry trends\n\n"
        "Provide balanced, well-reasoned investment recommendations with clear rationale."
    ),
    expected_output=(
        "An investment recommendation report containing:\n"
        "1. Investment thesis and key assumptions\n"
        "2. Valuation analysis and price targets\n"
        "3. Risk-reward assessment\n"
        "4. Recommended investment strategy\n"
        "5. Key risks and monitoring points"
    ),
    agent=investment_advisor,
    tools=[read_document_tool],
    async_execution=True,
    context=[financial_analysis_task]
)

# Risk Assessment Task
risk_assessment_task = Task(
    description=(
        "Conduct a thorough risk assessment of the investment opportunity presented in the "
        "document at {file_path}. The user's query is: {query}\n\n"
        "Evaluate the following risk categories:\n"
        "1. Market and industry risks\n"
        "2. Company-specific financial risks\n"
        "3. Operational and business model risks\n"
        "4. Regulatory and compliance risks\n"
        "5. Liquidity and capital structure risks\n\n"
        "Provide a balanced view of both upside potential and downside risks."
    ),
    expected_output=(
        "A comprehensive risk assessment report containing:\n"
        "1. Executive summary of key risks\n"
        "2. Detailed risk analysis by category\n"
        "3. Risk scoring and prioritization\n"
        "4. Mitigation strategies\n"
        "5. Overall risk rating and confidence level"
    ),
    agent=risk_assessor,
    tools=[read_document_tool],
    async_execution=True,
    context=[financial_analysis_task, investment_analysis_task]
)

# Main analysis task that coordinates all other tasks
analyze_financial_document = Task(
    description=(
        "Orchestrate the analysis of the financial document at {file_path} based on "
        "the user's query: {query}. This is a meta-task that will coordinate the work of "
        "specialist agents to provide a comprehensive analysis."
    ),
    expected_output=(
        "A consolidated financial analysis report containing:\n"
        "1. Document verification summary\n"
        "2. Detailed financial analysis\n"
        "3. Investment recommendations\n"
        "4. Comprehensive risk assessment\n"
        "5. Executive summary and key action items"
    ),
    agent=financial_analyst,  # This will be the orchestrator
    tools=[],
    async_execution=False,
    context=[
        document_verification_task,
        financial_analysis_task,
        investment_analysis_task,
        risk_assessment_task
    ]
)