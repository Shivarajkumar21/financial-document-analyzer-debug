## Importing libraries and files
import os
import re
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader
from crewai_tools.tools.serpapi_tool.serpapi_google_search_tool import SerpApiGoogleSearchTool

# Load environment variables
load_dotenv()

class FinancialDocumentTool:
    """Tool for reading and processing financial documents."""
    
    @staticmethod
    def _extract_metric(text: str, pattern: str, converter=float) -> Optional[float]:
        """
        Extract a metric from text using regex pattern.
        
        Args:
            text: Text to search in
            pattern: Regex pattern to find the metric
            converter: Function to convert the matched string to desired type
            
        Returns:
            Extracted and converted metric value, or None if not found
        """
        import re
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                # Extract the first group and clean it
                value_str = match.group(1).replace(',', '')
                return converter(value_str)
            except (IndexError, ValueError, AttributeError):
                return None
        return None
    
    @staticmethod
    def read_data_tool(file_path: str) -> str:
        """
        Read and process text from a PDF financial document.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Extracted and cleaned text from the document
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: For other processing errors
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            # Validate file extension
            if not file_path.lower().endswith('.pdf'):
                raise ValueError("Only PDF files are supported")
            
            # Read PDF content
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                full_text = []
                
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        # Clean up text
                        text = re.sub(r'\s+', ' ', text).strip()
                        full_text.append(text)
                        
                if not full_text:
                    raise ValueError("No text could be extracted from the PDF")
                    
                return '\n\n'.join(full_text)
                
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")

class InvestmentAnalysisTool:
    """Tool for analyzing investment opportunities from financial documents."""
    
    @staticmethod
    def analyze_investment(document_text: str) -> dict:
        """
        Analyze investment opportunities from financial document text.
        
        Args:
            document_text (str): Text content from a financial document
            
        Returns:
            dict: Analysis containing key metrics and recommendations
        """
        try:
            # Extract key financial metrics using regex patterns
            metrics = {
                'revenue': FinancialDocumentTool._extract_metric(document_text, r'revenue\s*[\$\£\€]?\s*([\d,]+(?:\.[\d]{2})?)', float),
                'net_income': FinancialDocumentTool._extract_metric(document_text, r'net\s*income\s*[\$\£\€]?\s*([\d,]+(?:\.[\d]{2})?)', float),
                'eps': FinancialDocumentTool._extract_metric(document_text, r'earnings\s*per\s*share\s*[\$\£\€]?\s*([\d,]+(?:\.[\d]{2})?)', float),
            }
            
            # Generate basic analysis
            analysis = {
                'financial_metrics': metrics,
                'recommendation': 'HOLD',  # Placeholder - would be determined by analysis
                'confidence_score': 0.75,  # Placeholder
                'key_findings': []
            }
            
            # Add basic analysis based on metrics
            if 'revenue' in metrics and 'net_income' in metrics:
                if metrics['revenue'] > 0 and metrics['net_income'] > 0:
                    profit_margin = (metrics['net_income'] / metrics['revenue']) * 100
                    analysis['profit_margin'] = f"{profit_margin:.2f}%"
                    
                    if profit_margin > 20:
                        analysis['key_findings'].append("Strong profitability with high profit margin")
                    elif profit_margin > 10:
                        analysis['key_findings'].append("Moderate profitability")
                    else:
                        analysis['key_findings'].append("Low profit margins detected")
            
            return analysis
            
        except Exception as e:
            return {
                'error': f"Error in investment analysis: {str(e)}",
                'recommendation': 'Unable to determine',
                'confidence_score': 0.0
            }

class RiskAssessmentTool:
    """Tool for assessing financial risks from document analysis."""
    
    @staticmethod
    def assess_risk(document_text: str) -> dict:
        """
        Assess financial risks based on document analysis.
        
        Args:
            document_text (str): Text content from a financial document
            
        Returns:
            dict: Risk assessment with severity levels and mitigation strategies
        """
        try:
            # Simple risk indicators (in a real system, this would be more sophisticated)
            risk_keywords = {
                'high': ['bankruptcy', 'default', 'liquidation', 'fraud', 'lawsuit'],
                'medium': ['risk', 'volatility', 'uncertainty', 'competition', 'regulation'],
                'low': ['growth', 'opportunity', 'stable', 'diversified']
            }
            
            # Count risk indicators
            risk_counts = {'high': 0, 'medium': 0, 'low': 0}
            
            for level, keywords in risk_keywords.items():
                for keyword in keywords:
                    risk_counts[level] += document_text.lower().count(keyword.lower())
            
            # Determine overall risk level
            if risk_counts['high'] > 0:
                overall_risk = 'High'
            elif risk_counts['medium'] > 2:
                overall_risk = 'Medium'
            else:
                overall_risk = 'Low'
            
            return {
                'overall_risk': overall_risk,
                'risk_factors': risk_counts,
                'mitigation_strategies': [
                    'Diversify investment portfolio',
                    'Conduct thorough due diligence',
                    'Consult with financial advisor'
                ]
            }
            
        except Exception as e:
            return {
                'error': f"Error in risk assessment: {str(e)}",
                'overall_risk': 'Unknown'
            }

# Initialize search tool
search_tool = SerpApiGoogleSearchTool()